from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.prescription import Medicine, Prescription
from app.models.user import UserRole
from app.schemas.prescription import PrescriptionCreate, PrescriptionOut, PrescriptionUpdate
from app.utils.deps import CurrentUserDep
from app.utils.permissions import role_required

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


# ── Create ───────────────────────────────────────────────────
@router.post("/", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
def create_prescription(
    data: PrescriptionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR])),
):
    prescription = Prescription(
        patient_id=data.patient_id,
        notes=data.notes,
        doctor_id=current_user.id,
    )
    db.add(prescription)
    db.flush()  # get the ID before adding medicines

    for med in data.medicines:
        db.add(Medicine(**med.model_dump(), prescription_id=prescription.id))

    db.commit()
    db.refresh(prescription)

    db.add(AuditLog(user_id=current_user.id, action="CREATE", resource="prescription", resource_id=prescription.id))
    db.commit()
    return prescription


# ── List (with pagination) ──────────────────────────────────
@router.get("/", response_model=list[PrescriptionOut])
def get_prescriptions(
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    patient_id: Annotated[int | None, Query()] = None,
):
    query = db.query(Prescription).filter(Prescription.doctor_id == current_user.id)

    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)

    return query.order_by(Prescription.created_at.desc()).offset(skip).limit(limit).all()


# ── Get by ID ────────────────────────────────────────────────
@router.get("/{prescription_id}", response_model=PrescriptionOut)
def get_prescription(
    prescription_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
):
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.doctor_id == current_user.id,
    ).first()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    return prescription


# ── Update (notes only — medicines are immutable per prescription) ─
@router.put("/{prescription_id}", response_model=PrescriptionOut)
def update_prescription(
    prescription_id: int,
    data: PrescriptionUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR])),
):
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.doctor_id == current_user.id,
    ).first()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prescription, field, value)

    db.commit()
    db.refresh(prescription)

    db.add(AuditLog(user_id=current_user.id, action="UPDATE", resource="prescription", resource_id=prescription.id))
    db.commit()
    return prescription


# ── Delete ───────────────────────────────────────────────────
@router.delete("/{prescription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prescription(
    prescription_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR])),
):
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.doctor_id == current_user.id,
    ).first()
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")

    db.add(AuditLog(user_id=current_user.id, action="DELETE", resource="prescription", resource_id=prescription.id))
    db.delete(prescription)  # cascade deletes medicines
    db.commit()