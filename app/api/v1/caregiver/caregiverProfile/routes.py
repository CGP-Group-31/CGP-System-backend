from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import *
from .repository import(get_caregiver_profile,update_caregiver_profile,deactivate_account, if_caregiver_exist)


router= APIRouter(prefix="/caregiver-profile", tags=["Caregiver Profile"])

@router.get("/", response_model=CaregiverProfileResponse)
def get_profile(caregiver_id: int, db: Session = Depends(get_db)):
    if caregiver_id<=0:
        raise HTTPException(status_code=422, detail="Caregiver id must be greater than 0")
    
    if not if_caregiver_exist(db, caregiver_id):
        raise HTTPException(status_code=404, detail="Caregiver does not exist")
    
    profile = get_caregiver_profile(db, caregiver_id)
    return profile


@router.patch("/{caregiver_id}")
def update_profile(caregiver_id: int, data: CaregiverProfileUpdate, db: Session = Depends(get_db)):
    if caregiver_id<=0:
        raise HTTPException(status_code=422, detail="Caregiver id must be greater than 0")
    
    if not if_caregiver_exist(db, caregiver_id):
        raise HTTPException(status_code=404, detail="Caregiver does not exist")
    
    updated = update_caregiver_profile(db,caregiver_id,data)

    if updated == "no_fields":
        raise HTTPException(status_code=400, detail="No fields provided")
    if updated == "no_fields":
        raise HTTPException(status_code=404, detail="Caregiver not found")
    db.commit()
    return {"message": "Profile updated successfully"}


#keep or remove??
@router.delete("/{caregiver_id}")
def deactivate_acc(caregiver_id: int, db: Session = Depends(get_db)):
    if caregiver_id<=0:
        raise HTTPException(status_code=422, detail="Caregiver id must be greater than 0")
    
    if not if_caregiver_exist(db, caregiver_id):
        raise HTTPException(status_code=404, detail="Caregiver does not exist")
    
    deactivate_account(db, caregiver_id)
    db.commit()
    return{"message":"Account deactivated successfully"}