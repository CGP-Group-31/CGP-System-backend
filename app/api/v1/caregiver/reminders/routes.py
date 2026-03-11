from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from .repository import (
    get_today_scheduled_for_reminders,
    get_today_taken_for_reminders,
    get_today_missed_for_reminders,
)
from .schemas import TodayMedsResponse

router = APIRouter(prefix="/medicine", tags=["Reminders"])


@router.get("/elder/{elder_id}/today-scheduled", response_model=list[TodayMedsResponse])
def api_tdy_scheduled(elder_id: int, db: Session = Depends(get_db)):
    return get_today_scheduled_for_reminders(db, elder_id)


@router.get("/elder/{elder_id}/today-taken", response_model=list[TodayMedsResponse])
def api_tdy_taken(elder_id: int, db: Session = Depends(get_db)):
    return get_today_taken_for_reminders(db, elder_id)


@router.get("/elder/{elder_id}/today-missed", response_model=list[TodayMedsResponse])
def api_tdy_missed(elder_id: int, db: Session = Depends(get_db)):
    return get_today_missed_for_reminders(db, elder_id)