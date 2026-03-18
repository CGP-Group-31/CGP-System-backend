from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from .repository import get_daily_medication_summary,get_daily_meal_summary

from .schemas import MedicationReportResponse,MealReportResponse


router = APIRouter(prefix="/daily-reports", tags=["Daily Reports"])


@router.get("/elder/{elder_id}/medication", response_model=MedicationReportResponse)
def get_medication(elder_id: int, date: date, db: Session = Depends(get_db)):
    return get_daily_medication_summary(db, elder_id, date)


@router.get("/elder/{elder_id}/meals", response_model=MealReportResponse)
def get_meals(elder_id: int, date: date, db: Session = Depends(get_db)):
    return get_daily_meal_summary(db, elder_id, date)