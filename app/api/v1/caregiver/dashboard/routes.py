from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import *

from app.core.database import get_db
from .repository import get_caregiver_name, missed_tdy_count, upcoming_appointment_count

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/elder/{elder_id}/name", response_model=CaregiverNameResponse)
def caregiver_name(caregiver_id: int, db:Session=Depends(get_db)):
    name= get_caregiver_name(db,caregiver_id)
    if not name:
        raise HTTPException(status_code=404, detail="Caregiver not found")
    return{"caregiver_id": caregiver_id, "full_name": name}

@router.get("/elder/{elder_id}/medication/missed-today-count", response_model=MissedMedicationCountResponse)
def missed_today(elder_id: int, db:Session=Depends(get_db)):
    cnt= missed_tdy_count(db,elder_id)
    return{"elder_id": elder_id, "missed_tdy_count": cnt}

@router.get("/elder/{elder_id}/appointments/upcoming-count", response_model=UpcomingAppointmentCountResponse)
def upcoming_appointments_7_days(elder_id: int, db:Session=Depends(get_db)):
    cnt= upcoming_appointment_count(db,elder_id)
    return{"elder_id": elder_id, "upcoming_count": cnt}

