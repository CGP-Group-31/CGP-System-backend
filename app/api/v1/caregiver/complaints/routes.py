from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from .schemas import ComplaintCreateRequest, MessageResponse
from .repository import create_complaint

router = APIRouter(prefix="/complaints", tags=["Caregiver Complaints"])


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_complaint(
    data: ComplaintCreateRequest,
    db: Session = Depends(get_db)
):
    success, error = create_complaint(db, data)

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {"message": "Complaint submitted successfully"}