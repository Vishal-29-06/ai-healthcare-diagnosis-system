from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.availability import DoctorAvailability, Weekday
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentStatusUpdate
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/appointments", tags=["Appointments"])

# Fixed slot length. A real system might make this configurable per
# doctor/specialty — we're keeping it simple and explainable.
SLOT_DURATION = timedelta(minutes=30)

# Python's datetime.weekday() returns 0=Monday...6=Sunday.
# This maps that number to our Weekday enum so we can compare against
# what's stored in doctor_availabilities.
WEEKDAY_MAP = {
    0: Weekday.MONDAY,
    1: Weekday.TUESDAY,
    2: Weekday.WEDNESDAY,
    3: Weekday.THURSDAY,
    4: Weekday.FRIDAY,
    5: Weekday.SATURDAY,
    6: Weekday.SUNDAY,
}


@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PATIENT)),
):
    """
    Patient-only: books a new appointment, after validating:
    1. The requested time is in the future.
    2. It falls inside one of the doctor's availability windows.
    3. That exact slot isn't already booked by someone else.
    """
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()

    doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
    if not doctor or not doctor.is_approved:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if payload.scheduled_at <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment time must be in the future.",
        )

    requested_weekday = WEEKDAY_MAP[payload.scheduled_at.weekday()]
    requested_time = payload.scheduled_at.time()
    slot_end_time = (payload.scheduled_at + SLOT_DURATION).time()

    matching_slot = (
        db.query(DoctorAvailability)
        .filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.day_of_week == requested_weekday,
            DoctorAvailability.start_time <= requested_time,
            DoctorAvailability.end_time >= slot_end_time,
        )
        .first()
    )
    if not matching_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This doctor is not available at the requested time.",
        )

    conflict = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor.id,
            Appointment.scheduled_at == payload.scheduled_at,
            Appointment.status != AppointmentStatus.CANCELLED,
        )
        .first()
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This slot is already booked.",
        )

    new_appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        scheduled_at=payload.scheduled_at,
        reason=payload.reason,
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


@router.get("/my", response_model=list[AppointmentOut])
def my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Works for BOTH patients and doctors — returns whichever list is
    relevant based on the logged-in user's role. This is why we use
    get_current_user here (any logged-in role) instead of require_role.
    """
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        return db.query(Appointment).filter(Appointment.patient_id == patient.id).all()

    if current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        return db.query(Appointment).filter(Appointment.doctor_id == doctor.id).all()

    raise HTTPException(status_code=403, detail="Not applicable for this role.")


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
):
    """Doctor-only: confirm, complete, or cancel an appointment booked with them."""
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.doctor_id == doctor.id)
        .first()
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    appointment.status = payload.status
    db.commit()
    db.refresh(appointment)
    return appointment
