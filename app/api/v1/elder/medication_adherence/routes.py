from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from app.core.database import get_db

router = APIRouter(prefix="/medication-adherence", tags=["MedicationAdherence"])


class MarkTakenRequest(BaseModel):
    scheduleId: int
    elderId: int
    scheduledFor: str  


@router.post("/taken")
def mark_taken(data: MarkTakenRequest, db: Session = Depends(get_db)):
    try:
        # accept "2026-02-28T17:06:00" and also "2026-02-28T17:06:00+05:30"
        sf = data.scheduledFor.strip()
        sf_dt = datetime.fromisoformat(sf.replace("Z", "+00:00"))

        # If timezone included, drop tzinfo because DB column is DATETIME2 (no offset)
        if sf_dt.tzinfo is not None:
            sf_dt = sf_dt.replace(tzinfo=None)

        q = text("""UPDATE MedicationAdherence SET StatusID = 2, TakenAt = SYSDATETIME()
            WHERE ScheduleID = :sid
              AND ElderID = :eid
              AND ScheduledFor = :sf
              AND StatusID = 1;""")

        result = db.execute(q, {"sid": data.scheduleId, "eid": data.elderId, "sf": sf_dt})
        db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pending record not found (or already taken)")

        return {"message": "Marked as taken"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scheduledFor format")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while marking taken")