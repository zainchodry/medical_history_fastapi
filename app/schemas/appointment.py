import enum
from datetime import date, datetime, time
from typing import Optional

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
    reason: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    reason: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatusEnum


class AppointmentOut(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None