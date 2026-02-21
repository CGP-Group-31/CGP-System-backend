from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import *
from .repository import(get_caregiver_profile,update_caregiver_profile,deactivate_account)


router= APIRouter(prefix="/profile", tags=["Caregiver Profile"])

@router.get("/")
def get_profile(caregiver_id: int, db: Session = Depends(get_db) 
):
    profile = get_caregiver_profile(db, caregiver_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("/")
def update_profile(caregiver_Id: int, data: CaregiverProfileUpdate, db: Session = Depends(get_db)):
    updated = update_caregiver_profile(db,caregiver_Id,data) #current_user["UserID"]

    if not updated:
        raise HTTPException(status_code=400, detail="No fields provided")
    db.commit()
    return {"message": "Profile updated successfully"}

#keep or remove??
@router.delete("/")
def deactivate_acc(caregiver_id: int, db: Session = Depends(get_db) #, current_user=Depends(get_current_caregiver)
):
    deactivate_account(db, caregiver_id)
    db.commit()
    return{"message":"Account deactivated successfully"}