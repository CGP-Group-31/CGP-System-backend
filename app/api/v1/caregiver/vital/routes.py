import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from .schemas import VitalCreate, VitalResponse, VitalUpdate, GetVitalTypes
from .repository import create_vital_record, get_vitals, update_vitals, all_vital_types


router = APIRouter(prefix="/vitals",tags=["Elder Vitals"])

@router.post("/")
def add_vital_record( data: VitalCreate, db:Session = Depends(get_db)):
    create = create_vital_record(db, data)
    if not create:
        raise HTTPException(status_code=404, detail="Failed to create vital")
    db.commit()
    return{
        "message": "Vital record created successfully!"
    }


@router.get("/{elder_id}", response_model=VitalResponse)
def get_vital_record(elder_id: int, db: Session = Depends(get_db)):
    vital = get_vitals(db, elder_id)

    if not vital:
        raise HTTPException(status_code=404, detail="Vital record not found")
    return vital


@router.patch("/{record_id}", response_model=dict)
def update_vital_record(record_id: int, data: VitalUpdate, db: Session = Depends(get_db)):
    updated = update_vitals(db,record_id,data) 

    if updated == "no_fields":
        raise HTTPException(status_code=400, detail="No fields provided")
    if updated == "no_fields":
        raise HTTPException(status_code=404, detail="Caregiver not found")
    db.commit()
    return {"message": "Vital record updated successfully"}


@router.get("/all-vitals", response_model=GetVitalTypes)
def get_vital_record(db: Session = Depends(get_db)):
    vital = all_vital_types(db)

    if not vital:
        raise HTTPException(status_code=404, detail="No vital types found")
    return vital