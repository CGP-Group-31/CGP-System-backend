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

@router.get("/medical-profile/{elder_id}")
def get_elder_medical_data(elder_id: int,db: Session= Depends(get_db) #,current_user = Depends(verify_access_to_elder)
):
    profile= get_elder_profile(db, elder_id)
    if not profile:
        raise HTTPException(status_code=404)
    return profile

@router.patch("/{elder_id}")
def update_elder_details(elder_id: int,data: ElderUpdate,db: Session= Depends(get_db) #,current_user= Depends(verify_access_to_elder)
):
    updated = update_elder(db, elder_id, data)

    if not updated:
        raise HTTPException(status_code=404)
    
    db.commit()
    return{"message":"Elder updated successfully"}


@router.patch("/medical-profile/{elder_id}")
def update_elder_medical_data(elder_id: int,data: ElderProfileUpdate,db: Session= Depends(get_db) #,current_user= Depends(verify_access_to_elder)
):
    updated = update_elder_profile(db, elder_id, data)

    if not updated:
        raise HTTPException(status_code=404)
    
    db.commit()
    return{"message":"Elder medical details updated successfully"}