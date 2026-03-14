from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from .schemas import ComplaintResponse
from .repository import get_all_complaints

router = APIRouter(prefix="/complaints", tags=["Admin Complaints"])


@router.get(
    "",
    response_model=List[ComplaintResponse],
    status_code=status.HTTP_200_OK
)
def list_all_complaints(db: Session = Depends(get_db)):
    complaints, error = get_all_complaints(db)

    if error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error
        )

    return complaints or []