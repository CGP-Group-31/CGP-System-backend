from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .repository import *
from .schemas import *


router=APIRouter(prefix="/elder", tags=["Elder Management"])

    
@router.get("/{elder_id}", response_model=ElderDetailsResponse)
def get_elder_details(elder_id: int,db: Session= Depends(get_db) ):
    
    elder= get_elder(db, elder_id)
    if not elder:
        raise HTTPException(status_code=404)
    return elder

@router.get("/medical-profile/{elder_id}", response_model=ElderProfileResponse)
def get_elder_medical_data(elder_id: int,db: Session= Depends(get_db)):
    profile= get_elder_profile(db, elder_id)
    if not profile:
        raise HTTPException(status_code=404)
    return profile

@router.patch("/{elder_id}")
def update_elder_details(elder_id: int,data: ElderUpdate,db: Session= Depends(get_db) ):
    updated = update_elder(db, elder_id, data)

    if updated == "no_fields":
        raise HTTPException(status_code=400, detail="No fields provided")
    if updated == "not_found":
        raise HTTPException(status_code=404, detail="Elder not found")
    
    db.commit()
    return{"message":"Elder updated successfully"}

@router.get("/preferred-doctor/{elder_id}", response_model=PreferredDoctorResponse)
def get_preferred_doc(elder_id: int,db: Session= Depends(get_db)):
    doc= get_preferred_doctor(db, elder_id)
    if not doc:
        raise HTTPException(status_code=404)
    return doc

@router.patch("/preferred-doctor/{elder_id}")
def update_preferred_doc(elder_id: int,data: UpdatePreferredDoctor, db: Session= Depends(get_db)):
    updated = update_preferred_doctor(db, elder_id, data.preferred_doctor_id)
    
    if updated == "not_found":
        raise HTTPException(status_code=404, detail="Elder profile not found")
    db.commit()
    return{"message":"Doctor details updated successfully"}
