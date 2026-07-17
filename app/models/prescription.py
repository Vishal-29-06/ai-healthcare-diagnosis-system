from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Prescription(Base):
    """
    A single medicine entry tied to a medical record.
    One record can have many prescriptions (e.g. 3 different medicines
    from one visit) — that's why this doesn't have unique=True on
    record_id, unlike the one-to-one relationships above.
    """
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("medical_records.id"), nullable=False)

    medicine_name: Mapped[str] = mapped_column(String(150), nullable=False)
    dosage: Mapped[str] = mapped_column(String(50), nullable=True)
    frequency: Mapped[str] = mapped_column(String(50), nullable=True)
    duration: Mapped[str] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    medical_record = relationship("MedicalRecord", back_populates="prescriptions")
