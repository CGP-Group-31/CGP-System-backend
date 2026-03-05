# app/modules/medication/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text

from app.core.database import get_db
from .schemas import MedicationCreateRequest, MedicationCreateResponse, MedicationUpdateRequest
from .repository import (
    create_medication,
    create_medication_schedules,
    get_medications_by_elder,
    update_medication,
    update_medication_schedules,
    deactivate_medication
)

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
        raise HTTPException(status_code=400, detail=str(getattr(e, "orig", e)))

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(getattr(e, "orig", e)))


@router.get("/elder/{elder_id}")
def get_medication_list(elder_id: int, db: Session = Depends(get_db)):

    try:
        return get_medications_by_elder(db, elder_id)

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{medication_id}")
def update_medication_api(
    medication_id: int,
    data: MedicationUpdateRequest,
    db: Session = Depends(get_db)
):

    try:

        update_medication(db, medication_id, data)

        update_medication_schedules(
            db=db,
            medication_id=medication_id,
            times=data.times,
            repeat_days=data.repeatDays,
            start_date=data.startDate,
            end_date=data.endDate
        )

        db.commit()

        return {"message": "Medication updated successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{medication_id}")
def delete_medication(medication_id: int, db: Session = Depends(get_db)):

    try:

        deactivate_medication(db, medication_id)

        db.commit()

        return {"message": "Medication deactivated"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{medication_id}")
def get_medication_by_id(medication_id: int, db: Session = Depends(get_db)):

    try:

        rows = db.execute(
            text("""
                SELECT 
                    m.MedicationID,
                    m.MedicationName,
                    m.Dosage,
                    m.Instructions,
                    s.TimeOfDay,
                    s.RepeatDays,
                    s.StartDate,
                    s.EndDate
                FROM Medications m
                JOIN MedicationSchedules s 
                    ON m.MedicationID = s.MedicationID
                WHERE 
                    m.IsActive = 1
                    AND s.IsActive = 1
                    AND m.MedicationID = :id
                ORDER BY s.TimeOfDay
            """),
            {"id": medication_id}
        ).fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="Medication not found")

        times = [
            r.TimeOfDay.strftime("%H:%M")
            for r in rows
        ]

        first = rows[0]

        return {
            "medicationId": first.MedicationID,
            "name": first.MedicationName,
            "dosage": first.Dosage,
            "instructions": first.Instructions,
            "times": times,
            "repeatDays": first.RepeatDays,
            "startDate": first.StartDate,
            "endDate": first.EndDate
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))