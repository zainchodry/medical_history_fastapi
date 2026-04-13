from datetime import date, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.user import UserRole
from app.utils.deps import CurrentUserDep
from app.utils.permissions import role_required

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Annotated[Session, Depends(get_db)],
    current_user=Depends(role_required([UserRole.DOCTOR, UserRole.ADMIN])),
):
    """Return aggregate statistics for the doctor's dashboard."""
    today = date.today()

    total_patients = db.query(func.count(Patient.id)).filter(
        Patient.user_id == current_user.id
    ).scalar() or 0

    total_appointments = db.query(func.count(Appointment.id)).filter(
        Appointment.doctor_id == current_user.id
    ).scalar() or 0

    today_appointments = db.query(func.count(Appointment.id)).filter(
        Appointment.doctor_id == current_user.id,
        Appointment.date == today,
        Appointment.status == "scheduled",
    ).scalar() or 0

    upcoming_appointments = db.query(func.count(Appointment.id)).filter(
        Appointment.doctor_id == current_user.id,
        Appointment.date >= today,
        Appointment.status == "scheduled",
    ).scalar() or 0

    total_records = db.query(func.count(MedicalRecord.id)).filter(
        MedicalRecord.doctor_id == current_user.id
    ).scalar() or 0

    total_prescriptions = db.query(func.count(Prescription.id)).filter(
        Prescription.doctor_id == current_user.id
    ).scalar() or 0

    # Recent patients (last 5)
    recent_patients = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .order_by(Patient.created_at.desc())
        .limit(5)
        .all()
    )

    # Today's appointment list
    todays_list = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == current_user.id,
            Appointment.date == today,
        )
        .order_by(Appointment.start_time)
        .all()
    )

    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming_appointments,
        "total_medical_records": total_records,
        "total_prescriptions": total_prescriptions,
        "recent_patients": [
            {"id": p.id, "full_name": p.full_name, "gender": p.gender}
            for p in recent_patients
        ],
        "todays_schedule": [
            {
                "id": a.id,
                "patient_id": a.patient_id,
                "start_time": str(a.start_time),
                "end_time": str(a.end_time),
                "status": a.status.value if hasattr(a.status, "value") else a.status,
            }
            for a in todays_list
        ],
    }
