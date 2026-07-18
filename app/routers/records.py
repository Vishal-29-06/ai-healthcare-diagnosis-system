from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.prescription import Prescription
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordOut,
    PrescriptionCreate,
    PrescriptionOut,
)
from app.core.dependencies import get_current_user, require_role

router = APIRouter(tags=["Medical Records"])


def _get_record_or_403(record_id: int, current_user: User, db: Session) -> MedicalRecord:
    """
    Shared ownership check, reused by every record/prescription route
    below. A record can only be viewed/edited by:
      - the patient it belongs to, or
      - the doctor who conducted that appointment.
    Anyone else gets 403, even if they're logged in as SOME
    patient/doctor — this is the IDOR protection pattern again.
    """
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found.")

    appointment = record.appointment

    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not your medical record.")

    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or appointment.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Not your patient's record.")

    return record


@router.post(
    "/appointments/{appointment_id}/records",
    response_model=MedicalRecordOut,
    status_code=status.HTTP_201_CREATED,
)
def create_medical_record(
    appointment_id: int,
    payload: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
):
    """
    Doctor-only: add diagnosis/notes for an appointment they conducted.
    We check appointment.doctor_id against the LOGGED-IN doctor, not
    a value the client could send us — same ownership pattern as
    everywhere else.
    """
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id, Appointment.doctor_id == doctor.id)
        .first()
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    if appointment.medical_record is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A medical record already exists for this appointment.",
        )

    record = MedicalRecord(appointment_id=appointment.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/records/my", response_model=list[MedicalRecordOut])
def my_medical_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PATIENT)),
):
    """Patient-only: every medical record tied to any of their appointments."""
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()

    return (
        db.query(MedicalRecord)
        .join(Appointment)
        .filter(Appointment.patient_id == patient.id)
        .all()
    )


@router.get("/records/{record_id}", response_model=MedicalRecordOut)
def get_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_record_or_403(record_id, current_user, db)


@router.post(
    "/records/{record_id}/prescriptions",
    response_model=PrescriptionOut,
    status_code=status.HTTP_201_CREATED,
)
def add_prescription(
    record_id: int,
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
):
    """Doctor-only: attach a prescription to a record (reuses the ownership check)."""
    record = _get_record_or_403(record_id, current_user, db)

    prescription = Prescription(record_id=record.id, **payload.model_dump())
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return prescription
