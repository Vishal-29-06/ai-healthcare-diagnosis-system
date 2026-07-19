from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.schemas.admin import AdminStats, PendingDoctorOut
from app.core.dependencies import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])

# Every route in this file uses this same dependency — admin-only,
# no exceptions. Defined once here to avoid repeating it on every route.
admin_only = Depends(require_role(UserRole.ADMIN))


@router.get("/stats", response_model=AdminStats)
def get_stats(db: Session = Depends(get_db), _admin: User = admin_only):
    """A quick system-wide overview — the numbers a hospital admin dashboard would open on."""
    return AdminStats(
        total_patients=db.query(Patient).count(),
        total_doctors=db.query(Doctor).count(),
        pending_doctor_approvals=db.query(Doctor).filter(Doctor.is_approved == False).count(),  # noqa: E712
        total_appointments=db.query(Appointment).count(),
        total_medical_records=db.query(MedicalRecord).count(),
    )


@router.get("/doctors/pending", response_model=list[PendingDoctorOut])
def list_pending_doctors(db: Session = Depends(get_db), _admin: User = admin_only):
    """Doctors who've signed up but haven't been approved to start accepting appointments yet."""
    pending = db.query(Doctor).filter(Doctor.is_approved == False).all()  # noqa: E712
    return [
        PendingDoctorOut(
            doctor_id=d.id,
            user_id=d.user_id,
            full_name=d.user.full_name,
            email=d.user.email,
            specialization=d.specialization,
        )
        for d in pending
    ]


@router.patch("/doctors/{doctor_id}/approve")
def approve_doctor(doctor_id: int, db: Session = Depends(get_db), _admin: User = admin_only):
    """This is what replaces the manual SQL UPDATE we were doing before."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")

    doctor.is_approved = True
    db.commit()
    return {"message": f"Doctor {doctor.user.full_name} approved."}


@router.patch("/users/{user_id}/toggle-active")
def toggle_user_active(user_id: int, db: Session = Depends(get_db), _admin: User = admin_only):
    """
    Flips a user's active status — this is how an admin suspends a
    misbehaving account, or reinstates one. Login already checks
    is_active (back in Phase 3), so a deactivated user is immediately
    locked out on their next login attempt.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_active = not user.is_active
    db.commit()
    return {"message": f"{user.full_name} is now {'active' if user.is_active else 'inactive'}."}
