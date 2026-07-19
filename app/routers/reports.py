import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.pdf_generator import generate_medical_report_pdf
from app.routers.records import _get_record_or_403

router = APIRouter(tags=["Reports"])


@router.get("/records/{record_id}/report")
def download_report(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Streams a PDF version of a medical record. Reuses the same
    ownership check as viewing the record on-screen — if you can't
    see it, you can't download it either.
    """
    record = _get_record_or_403(record_id, current_user, db)
    appointment = record.appointment
    patient_user = appointment.patient.user
    doctor_user = appointment.doctor.user

    # Assemble the plain dict our PDF generator expects — this
    # translation step is exactly why we designed the generator to
    # take a dict rather than raw ORM objects, keeping it reusable.
    report_data = {
        "patient_name": patient_user.full_name,
        "patient_email": patient_user.email,
        "doctor_name": doctor_user.full_name,
        "doctor_specialization": appointment.doctor.specialization,
        "appointment_date": appointment.scheduled_at.strftime("%Y-%m-%d %H:%M"),
        "diagnosis": record.diagnosis,
        "notes": record.notes,
        "risk_label": (
            "High risk" if (record.risk_score or 0) >= 0.5 else "Low risk"
        )
        if record.risk_score is not None
        else None,
        "risk_probability": record.risk_score,
        "top_factors": json.loads(record.risk_explanation)
        if record.risk_explanation
        else [],
        "prescriptions": [
            {
                "medicine_name": p.medicine_name,
                "dosage": p.dosage,
                "frequency": p.frequency,
                "duration": p.duration,
            }
            for p in record.prescriptions
        ],
    }

    pdf_buffer = generate_medical_report_pdf(report_data)

    filename = f"medical_report_{record_id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
