from datetime import datetime, time, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from .repository import get_vitals_for_elder_in_range
from .schemas import ElderVitalsLastWeekResponse

router = APIRouter(prefix="/vitals", tags=["AI System"])


@router.get("/elder/{elder_id}/last-week", response_model=ElderVitalsLastWeekResponse)
def get_elder_vitals_last_week(
    elder_id: int,
    db: Session = Depends(get_db),
):
    today = datetime.now().date()
    current_week_monday = today - timedelta(days=today.isoweekday() - 1)
    end_dt = datetime.combine(current_week_monday, time.min)
    start_dt = end_dt - timedelta(days=7)
    week_start_date = start_dt.date()
    week_end_date = (end_dt - timedelta(days=1)).date()

    rows = get_vitals_for_elder_in_range(
        db=db,
        elder_id=elder_id,
        start_dt=start_dt,
        end_dt=end_dt,
    )

    records = [
        {
            "record_id": r["RecordID"],
            "elder_id": r["ElderID"],
            "vital_name": r["VitalName"],
            "unit": r["Unit"],
            "value": float(r["Value"]),
            "notes": r["Notes"],
            "recorded_at": r["RecordedAt"],
        }
        for r in rows
    ]

    return {
        "status": "ok",
        "elder_id": elder_id,
        "week_start_date": week_start_date,
        "week_end_date": week_end_date,
        "records": records,
    }
