import enum
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    """
    An Enum restricts a column to a fixed set of allowed values.
    This means the database itself will reject "docotr" (typo) or
    "Doctor" (wrong case) — it can ONLY ever be one of these three.
    """
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class User(Base):
    """
    This is the single login/identity table for EVERYONE — patients,
    doctors, and admins all have a row here. Role-specific details
    (like a doctor's specialization) live in separate tables that
    link back to this one via user_id.
    """
    __tablename__ = "users"

    # Mapped[int] tells SQLAlchemy (and your editor) this column is
    # an integer. primary_key=True means this uniquely identifies each row.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # unique=True means the database will REJECT a second user with
    # the same email — this enforces "one account per email" at the
    # database level, not just in our Python code.
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)

    # We NEVER store a plain-text password. This column holds a
    # bcrypt hash (created in Phase 3) — even if the database were
    # ever leaked, the real passwords wouldn't be exposed.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # server_default=func.now() means MySQL itself stamps the time
    # when the row is created — we don't have to set it manually.
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # These "relationship" lines don't create columns — they let you
    # write python_user.patient_profile or python_user.doctor_profile
    # and SQLAlchemy automatically fetches the linked row for you.
    # uselist=False means "expect at most one" (a user is only ever
    # ONE role's profile, not a list of them).
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
