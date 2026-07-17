import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(Base):
    """
    The link between one Patient and one Doctor at a specific time.
    This is a 'many-to-many made concrete' — a Patient can book many
    Doctors over time, and a Doctor sees many Patients, so this table
    sits in between and records each individual booking.
    """
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)

    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.PENDING
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

    # One appointment produces at most one medical record (the notes
    # from that specific visit).
    medical_record = relationship(
        "MedicalRecord", back_populates="appointment", uselist=False
    )
