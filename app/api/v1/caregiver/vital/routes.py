import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from .schemas import VitalCreate, VitalResponse
from .repository import create_vital_record
#from app.core.authorization import get_current_caregiver, caregiver_has_access

router = APIRouter(prefix="/vitals",tags=["Elder Vitals"])

@router.post("/add", response_model=VitalResponse)
def add_vital_record(caregiver_id: int, data: VitalCreate, db:Session = Depends(get_db), #current_user= Depends(get_current_caregiver)
):

    """
    if not caregiver_has_access(db, current_user["UserID"], data.elderId):
        raise HTTPException(status_code=403, detail="Access denied")
    """
    try:
        record_ids = create_vital_record(db, data.dict())

        return VitalResponse(
            message="Vital record(s) created successfully!", recorded_ids= record_ids
        )
    
    except SQLAlchemyError as e:
        logging.error(str(e))
        raise HTTPException (
            status_code= 500 , detail="Database error while inserting vital record"
        )