from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.patient import Patient
from app.models.user import UserRole
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.utils.deps import CurrentUserDep
from app.utils.permissions import role_required

router = APIRouter(prefix="/patients", tags=["Patients"])


# ── Create ───────────────────────────────────────────────────
@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(
    data: PatientCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
):
    patient = Patient(**data.model_dump(), user_id=current_user.id)
    db.add(patient)
    db.commit()
    db.refresh(patient)

    db.add(AuditLog(user_id=current_user.id, action="CREATE", resource="patient", resource_id=patient.id))
    db.commit()
    return patient


# ── List (with search & pagination) ─────────────────────────
@router.get("/", response_model=list[PatientOut])
def get_patients(
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=100)] = None,
    gender: Annotated[str | None, Query()] = None,
    blood_type: Annotated[str | None, Query()] = None,
):
    query = db.query(Patient).filter(Patient.user_id == current_user.id)

    if search:
        query = query.filter(Patient.full_name.ilike(f"%{search}%"))
    if gender:
        query = query.filter(Patient.gender == gender)
    if blood_type:
        query = query.filter(Patient.blood_type == blood_type)

    return query.order_by(Patient.full_name).offset(skip).limit(limit).all()


# ── Get by ID ────────────────────────────────────────────────
@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.user_id == current_user.id,
    ).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient


# ── Update ───────────────────────────────────────────────────
@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.user_id == current_user.id,
    ).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    db.add(AuditLog(user_id=current_user.id, action="UPDATE", resource="patient", resource_id=patient.id))
    db.commit()
    return patient


# ── Delete ───────────────────────────────────────────────────
@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.user_id == current_user.id,
    ).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    db.add(AuditLog(user_id=current_user.id, action="DELETE", resource="patient", resource_id=patient.id))
    db.delete(patient)
    db.commit()
