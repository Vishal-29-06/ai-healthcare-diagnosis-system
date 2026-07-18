import enum

from sqlalchemy import ForeignKey, Enum, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Weekday(str, enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class DoctorAvailability(Base):
    """
    One row = 'this doctor is available on this weekday, between
    these two times.' A doctor can have many rows (e.g. one for
    each day they work).
    """
    __tablename__ = "doctor_availabilities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)

    day_of_week: Mapped[Weekday] = mapped_column(Enum(Weekday), nullable=False)

    # Time (not DateTime) — we only care about the clock time,
    # e.g. 09:00 to 17:00, repeating every matching weekday.
    start_time: Mapped[object] = mapped_column(Time, nullable=False)
    end_time: Mapped[object] = mapped_column(Time, nullable=False)

    doctor = relationship("Doctor", back_populates="availability_slots")
