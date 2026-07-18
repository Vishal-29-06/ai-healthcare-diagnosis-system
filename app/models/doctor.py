from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Doctor(Base):
    """
    Role-specific data for users whose role is 'doctor'.
    """
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    bio: Mapped[str] = mapped_column(String(500), nullable=True)

    # Doctors need admin approval before they can accept appointments
    # (this is the "Approve/reject doctor registrations" admin feature).
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor")
    availability_slots = relationship("DoctorAvailability", back_populates="doctor")
