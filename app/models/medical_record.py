from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class MedicalRecord(Base):
    """
    The doctor's notes from a specific appointment: diagnosis,
    observations, and (later) the ML-predicted risk score.
    """
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # unique=True because each appointment produces exactly one record.
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id"), unique=True, nullable=False
    )

    diagnosis: Mapped[str] = mapped_column(String(255), nullable=True)

    # Text (vs String) has no length limit — good for long free-form notes.
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # These two columns will be filled in by our ML model in Phase 6/7.
    risk_score: Mapped[float] = mapped_column(nullable=True)
    risk_explanation: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    appointment = relationship("Appointment", back_populates="medical_record")

    # One medical record can have several prescriptions attached to it.
    prescriptions = relationship("Prescription", back_populates="medical_record")
