from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.appointment import Appointment
from app.models.user import UserRole
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentStatusUpdate,
    AppointmentUpdate,
)
from app.utils.deps import CurrentUserDep
from app.utils.permissions import role_required

router = APIRouter(prefix="/appointments", tags=["Appointments"])


# ── Create ───────────────────────────────────────────────────
@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(
    data: AppointmentCreate,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
):
    # Check for time-slot conflicts
    conflict = db.query(Appointment).filter(
        Appointment.doctor_id == data.doctor_id,
        Appointment.date == data.date,
        Appointment.start_time < data.end_time,
        Appointment.end_time > data.start_time,
        Appointment.status != "cancelled",
    ).first()

    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is already booked",
        )

    appointment = Appointment(**data.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    db.add(AuditLog(user_id=current_user.id, action="CREATE", resource="appointment", resource_id=appointment.id))
    db.commit()
    return appointment


# ── List (with filters & pagination) ────────────────────────
@router.get("/", response_model=list[AppointmentOut])
def get_appointments(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
):
    # Doctors see their appointments, patients see theirs
    if current_user.role == UserRole.DOCTOR or current_user.role == UserRole.ADMIN:
        query = db.query(Appointment).filter(Appointment.doctor_id == current_user.id)
    else:
        query = db.query(Appointment).filter(Appointment.patient_id == current_user.id)

    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    return query.order_by(Appointment.date.desc(), Appointment.start_time).offset(skip).limit(limit).all()


# ── Get by ID ────────────────────────────────────────────────
@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(
    appointment_id: int,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    # ensure the user owns this appointment
    if current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return appointment


# ── Update ───────────────────────────────────────────────────
@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.doctor_id == current_user.id,
    ).first()
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)

    db.add(AuditLog(user_id=current_user.id, action="UPDATE", resource="appointment", resource_id=appointment.id))
    db.commit()
    return appointment


# ── Update Status (cancel / complete / no-show) ─────────────
@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_appointment_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    # Doctors can set any status, patients can only cancel
    if current_user.role == UserRole.PATIENT:
        if data.status.value != "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients can only cancel appointments",
            )
        if appointment.patient_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    appointment.status = data.status
    db.commit()
    db.refresh(appointment)

    db.add(AuditLog(
        user_id=current_user.id,
        action="STATUS_CHANGE",
        resource="appointment",
        resource_id=appointment.id,
        details=f"Status changed to {data.status.value}",
    ))
    db.commit()
    return appointment


# ── Delete ───────────────────────────────────────────────────
@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.doctor_id == current_user.id,
    ).first()
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    db.add(AuditLog(user_id=current_user.id, action="DELETE", resource="appointment", resource_id=appointment.id))
    db.delete(appointment)
    db.commit()