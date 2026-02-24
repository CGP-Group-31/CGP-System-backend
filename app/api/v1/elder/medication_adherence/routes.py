from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/medication-adherence", tags=["MedicationAdherence"])


class MarkTakenRequest(BaseModel):
    scheduleId: int
    elderId: int
    scheduledFor: str  # ISO datetime string


@router.post("/taken")
def mark_taken(data: MarkTakenRequest, db: Session = Depends(get_db)):
    q = text("""UPDATE MedicationAdherence
        SET StatusID = 2,
            TakenAt = GETDATE()
        WHERE ScheduleID = :sid
          AND ElderID = :eid
          AND ScheduledFor = :sf
          AND StatusID = 1;

        SELECT @@ROWCOUNT AS affected;""")

    row = db.execute(q, {"sid": data.scheduleId, "eid": data.elderId, "sf": data.scheduledFor}).fetchone()
    db.commit()

    if not row or row.affected == 0:
        raise HTTPException(status_code=404, detail="Pending record not found (or already taken)")

    return {"message": "Marked as taken"}