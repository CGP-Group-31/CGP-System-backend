from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from .repository import get_last_10_care_reports
from .schemas import CareReportListResponse

router = APIRouter(prefix="/care-reports", tags=["Care Reports"])


@router.get("/latest/{elder_id}", response_model=CareReportListResponse, status_code=200)
def get_latest_care_reports_api(
    elder_id: int,
    db: Session = Depends(get_db)
):
    reports, error = get_last_10_care_reports(db, elder_id)

    if error:
        if error == "Elder not found.":
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=400, detail=error)

    return {"reports": reports}