# Importing every model here means that as soon as someone does
# "from app import models" (or Alembic scans this package), Python
# actually runs each model file, which registers that table with
# SQLAlchemy's Base.metadata. Without this, tables can silently
# get skipped when we generate migrations or call create_all().

from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment, AppointmentStatus
from app.models.medical_record import MedicalRecord
from app.models.prescription import Prescription
