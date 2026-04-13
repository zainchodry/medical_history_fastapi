from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MedicalRecordBase(BaseModel):
    patient_id: int
    title: str
    diagnosis: str | None = None
    treatment: str | None = None
    notes: str | None = None
    visit_date: date


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    title: str | None = None
    diagnosis: str | None = None
    treatment: str | None = None
    notes: str | None = None
    visit_date: date | None = None


class MedicalRecordOut(MedicalRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None