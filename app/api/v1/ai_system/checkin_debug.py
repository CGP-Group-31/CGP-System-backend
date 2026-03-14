from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.checking_scheduler import run_checkin_scheduler

router = APIRouter(prefix="/debug/checkin", tags=["CheckIn Debug"])


@router.post("/run-now")
async def run_now(db: Session = Depends(get_db)):
    data = run_checkin_scheduler(db)
    return {"triggered": data}