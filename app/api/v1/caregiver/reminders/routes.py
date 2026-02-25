from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from .repository import get_today_missed, get_today_scheduled, get_today_taken
from .schemas import TodayMedsResponse, TodayMedSummaryResponse

router = APIRouter(prefix="/medicine", tags=["Reminders"])

@router.get("/elder/{elder_id}/today-scheduled", response_model=list[TodayMedsResponse])
def api_tdy_scheduled(elder_id: int, db: Session = Depends(get_db)):
    return get_today_scheduled(db, elder_id)

@router.get("/elder/{elder_id}/today-taken", response_model=list[TodayMedsResponse])
def api_tdy_taken(elder_id: int, db: Session = Depends(get_db)):
    return get_today_taken(db, elder_id)

@router.get("/elder/{elder_id}/today-missed", response_model=list[TodayMedsResponse])
def api_tdy_missed(elder_id: int, db: Session = Depends(get_db)):
    return get_today_missed(db, elder_id)