from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.availability import DoctorAvailability
from app.schemas.availability import AvailabilityCreate, AvailabilityOut
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/")
def list_doctors(db: Session = Depends(get_db)):
    """
    Public-ish listing (any logged-in user can browse doctors) —
    only approved doctors show up, since is_approved=False means
    an admin hasn't verified them yet.
    """
    doctors = db.query(Doctor).filter(Doctor.is_approved == True).all()  # noqa: E712
    return [
        {
            "id": d.id,
            "full_name": d.user.full_name,
            "specialization": d.specialization,
            "experience_years": d.experience_years,
        }
        for d in doctors
    ]


@router.get("/{doctor_id}/availability", response_model=list[AvailabilityOut])
def get_doctor_availability(doctor_id: int, db: Session = Depends(get_db)):
    """Anyone logged in can view a doctor's weekly availability, to pick a slot."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor.availability_slots


@router.post(
    "/me/availability",
    response_model=AvailabilityOut,
    status_code=status.HTTP_201_CREATED,
)
def add_my_availability(
    payload: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
):
    """
    Doctor-only: add a weekly availability slot for yourself.
    Notice the route is /me/availability, not /{doctor_id}/availability —
    this way a doctor can ONLY ever edit their own schedule, since we
    look up their doctor profile from their token, not from a URL
    parameter they could tamper with.
    """
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()

    new_slot = DoctorAvailability(doctor_id=doctor.id, **payload.model_dump())
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    return new_slot
