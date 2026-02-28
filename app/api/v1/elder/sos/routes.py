from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.database import get_db
from .schemas import SOSTriggerRequest,SOSTriggerResponse
from .repository import create_sos_log

router = APIRouter(prefix="/sos", tags=["SOS Trigger"])

@router.post("/trigger", response_model=SOSTriggerResponse)
def trigger_sos(payload: SOSTriggerRequest, db: Session = Depends(get_db)):
    try:
        row = create_sos_log(
            db=db,
            elder_id=payload.elder_id,
            relationship_id=payload.relationship_id,
            trigger_type_id=payload.trigger_type_id,
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    if not row:
        raise HTTPException(status_code=500, detail="Failed to create SOS log")

    return {
        "status": "ok",
        "sos_id": row["SOSID"],
        "triggered_at": row["TriggeredAt"],
    }

