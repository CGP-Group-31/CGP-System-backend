
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from .schemas import CaregiverCreate, CaregiverCreateResponse
from .repository import create_caregiver

router = APIRouter(prefix="/auth", tags=["Caregivers"])

@router.post(
    "/register",
    response_model=CaregiverCreateResponse,
    status_code=status.HTTP_201_CREATED
)
def register_caregiver(
    data: CaregiverCreate,
    db: Session = Depends(get_db)
):
    try:
        user_id = create_caregiver(db, data)
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
