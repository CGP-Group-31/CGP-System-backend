import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db

from fastapi import APIRouter, Depends, HTTPException, Query

from .schemas import (VitalCreate,VitalCreateResponse,VitalTypesResponse,ElderVitalsLatestResponse,)
from .repository import (create_vital_record, get_latest_vitals_by_type, list_vital_types,)

router = APIRouter(prefix="/vitals", tags=["Elder Vitals"])

@router.get("/types", response_model=VitalTypesResponse)
def get_vital_types(db: Session = Depends(get_db)):
    rows = list_vital_types(db)
    return {
        "status": "ok",
        "types": [
            {
                "vital_type_id": r["VitalTypeID"],
                "vital_name": r["VitalName"],
                "unit": r["Unit"],
            }
            for r in rows
        ],
    }

@router.post("", response_model=VitalCreateResponse)
def add_vital_record(data: VitalCreate, db: Session = Depends(get_db)):
    try:
        row = create_vital_record(
            db=db,
            elder_id=data.elder_id,
            vital_type_id=data.vital_type_id,
            value=data.value,
            notes=data.notes,
            recorded_by=data.recorded_by,
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    if not row:
        raise HTTPException(status_code=500, detail="Failed to create vital record")

    return {
        "status": "ok",
        "record_id": row["RecordID"],
        "recorded_at": row["RecordedAt"],
    }

@router.get("/elder/{elder_id}/latest", response_model=ElderVitalsLatestResponse)
def get_elder_vitals_latest(
    elder_id: int,
    limit_per_type: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
):
    rows = get_latest_vitals_by_type(db=db, elder_id=elder_id, limit_per_type=limit_per_type)

    # group by VitalTypeID
    grouped = {}
    for r in rows:
        vt_id = r["VitalTypeID"]
        if vt_id not in grouped:
            grouped[vt_id] = {
                "vital_type_id": vt_id,
                "vital_name": r["VitalName"],
                "unit": r["Unit"],
                "last": [],
            }

        grouped[vt_id]["last"].append({
            "record_id": r["RecordID"],
            "elder_id": r["ElderID"],
            "vital_type_id": r["VitalTypeID"],
            "vital_name": r["VitalName"],
            "unit": r["Unit"],
            "value": float(r["Value"]),
            "notes": r["Notes"],
            "recorded_by": r["RecordedBy"],
            "recorded_at": r["RecordedAt"],
        })

    # If elder has no records -> return empty categories (still OK)
    categories = list(grouped.values())

    return {
        "status": "ok",
        "elder_id": elder_id,
        "limit_per_type": limit_per_type,
        "categories": categories,
    }