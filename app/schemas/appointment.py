import enum
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class AppointmentStatusEnum(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    date: date
    start_time: time
    end_time: time
    reason: str | None = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    reason: str | None = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatusEnum


class AppointmentOut(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None