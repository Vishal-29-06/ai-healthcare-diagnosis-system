from datetime import date

from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    """
    Role-specific data for users whose role is 'patient'.
    Only exists linked to exactly one User row.
    """
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # ForeignKey("users.id") is the actual database-level link.
    # unique=True enforces "one patient profile per user" (a
    # one-to-one relationship, not one-to-many).
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    blood_group: Mapped[str] = mapped_column(String(5), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)

    # The "other side" of the relationship — lets you write
    # python_patient.user to get back the linked User row.
    user = relationship("User", back_populates="patient_profile")

    # One patient can have MANY appointments — this is a one-to-many
    # relationship, so no uselist=False here (default is "a list").
    appointments = relationship("Appointment", back_populates="patient")
