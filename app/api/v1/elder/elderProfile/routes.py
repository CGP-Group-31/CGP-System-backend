from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import ElderProfileResponse, CaregiverRelatedResponse
from .repository import get_elder_profile_with_primary_caregiver, if_elder_exist


router= APIRouter(prefix="/elder-profile", tags=["Elder Profile"])

@router.get("/{elder_id}", response_model=ElderProfileResponse)
def get_elder_profile(elder_id: int, db: Session = Depends(get_db)):
    if elder_id<=0:
        raise HTTPException(status_code=422, detail="Elder id must be greater than 0")
    
    if not if_elder_exist(db, elder_id):
        raise HTTPException(status_code=404, detail="Elder does not exist")
    
    profile = get_elder_profile_with_primary_caregiver(db, elder_id)
    return profile


