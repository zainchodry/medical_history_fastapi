from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.medical_record import MedicalRecord
from app.models.user import UserRole
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordOut, MedicalRecordUpdate
from app.utils.deps import CurrentUserDep
from app.utils.permissions import role_required

router = APIRouter(prefix="/records", tags=["Medical Records"])


# ── Create ───────────────────────────────────────────────────
@router.post("/", response_model=MedicalRecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    data: MedicalRecordCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR])),
):
    record = MedicalRecord(**data.model_dump(), doctor_id=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)

    db.add(AuditLog(user_id=current_user.id, action="CREATE", resource="medical_record", resource_id=record.id))
    db.commit()
    return record


# ── List (with filters & pagination) ────────────────────────
@router.get("/", response_model=list[MedicalRecordOut])
def get_records(
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    patient_id: Annotated[int | None, Query()] = None,
    search: Annotated[str | None, Query(max_length=100)] = None,
):
    query = db.query(MedicalRecord).filter(MedicalRecord.doctor_id == current_user.id)

    if patient_id:
        query = query.filter(MedicalRecord.patient_id == patient_id)
    if search:
        query = query.filter(
            MedicalRecord.title.ilike(f"%{search}%")
            | MedicalRecord.diagnosis.ilike(f"%{search}%")
        )

    return query.order_by(MedicalRecord.visit_date.desc()).offset(skip).limit(limit).all()


# ── Get by ID ────────────────────────────────────────────────
@router.get("/{record_id}", response_model=MedicalRecordOut)
def get_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
):
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.doctor_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")
    return record


# ── Update ───────────────────────────────────────────────────
@router.put("/{record_id}", response_model=MedicalRecordOut)
def update_record(
    record_id: int,
    data: MedicalRecordUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR])),
):
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.doctor_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    db.add(AuditLog(user_id=current_user.id, action="UPDATE", resource="medical_record", resource_id=record.id))
    db.commit()
    return record


# ── Delete ───────────────────────────────────────────────────
@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR])),
):
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.doctor_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")

    db.add(AuditLog(user_id=current_user.id, action="DELETE", resource="medical_record", resource_id=record.id))
    db.delete(record)
    db.commit()