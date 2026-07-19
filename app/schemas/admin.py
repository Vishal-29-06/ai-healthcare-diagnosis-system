from pydantic import BaseModel


class AdminStats(BaseModel):
    total_patients: int
    total_doctors: int
    pending_doctor_approvals: int
    total_appointments: int
    total_medical_records: int


class PendingDoctorOut(BaseModel):
    doctor_id: int
    user_id: int
    full_name: str
    email: str
    specialization: str

    class Config:
        from_attributes = True
