# app/modules/medication/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.database import get_db
from .schemas import MedicationCreateRequest, MedicationCreateResponse
from .repository import create_medication, create_medication_schedules

router = APIRouter(prefix="/medication", tags=["Medication"])


@router.post("/create", response_model=MedicationCreateResponse, status_code=201)
def create_medication_api(data: MedicationCreateRequest, db: Session = Depends(get_db)):
    try:
        medication_id = create_medication(db, data)
        create_medication_schedules(
            db=db,
            medication_id=medication_id,
            times=data.times,
            repeat_days=data.repeatDays,
            start_date=data.startDate,
            end_date=data.endDate
        )
        db.commit()

        return {
            "medicationId": medication_id,
            "elderId": data.elderId,
            "name": data.name,
            "dosage": data.dosage,
            "instructions": data.instructions,
            "times": data.times,
            "repeatDays": data.repeatDays,
            "startDate": data.startDate,
            "endDate": data.endDate
        }

    except IntegrityError as e:
        db.rollback()
        # FK errors, truncation can also appear here depending on driver
        raise HTTPException(status_code=400, detail=str(getattr(e, "orig", e)))

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(getattr(e, "orig", e)))