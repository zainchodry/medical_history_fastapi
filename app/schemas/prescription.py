from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicineSchema(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str | None = None
    instructions: str | None = None


class MedicineOut(MedicineSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PrescriptionCreate(BaseModel):
    patient_id: int
    notes: str | None = None
    medicines: list[MedicineSchema]


class PrescriptionUpdate(BaseModel):
    notes: str | None = None


class PrescriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    notes: str | None = None
    medicines: list[MedicineOut] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None