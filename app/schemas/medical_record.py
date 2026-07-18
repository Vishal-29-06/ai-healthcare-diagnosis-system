from datetime import datetime

from pydantic import BaseModel


class PrescriptionCreate(BaseModel):
    medicine_name: str
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None


class PrescriptionOut(BaseModel):
    id: int
    medicine_name: str
    dosage: str | None
    frequency: str | None
    duration: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class MedicalRecordCreate(BaseModel):
    diagnosis: str | None = None
    notes: str | None = None


class MedicalRecordOut(BaseModel):
    id: int
    appointment_id: int
    diagnosis: str | None
    notes: str | None
    risk_score: float | None
    risk_explanation: str | None
    created_at: datetime
    prescriptions: list[PrescriptionOut] = []

    class Config:
        from_attributes = True
