from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from .repository import (
    get_last_10_care_reports,
    list_care_reports,
    get_care_report_detail,
)
from .schemas import CareReportListResponse, CareReportDetailResponse

router = APIRouter(prefix="/care-reports", tags=["Care Reports"])

@router.get("/latest/{elder_id}", response_model=CareReportListResponse, status_code=200)
def get_latest_care_reports_api(
    elder_id: int,
    db: Session = Depends(get_db)
):
    data, error = get_last_10_care_reports(db, elder_id)

    if error:
        if error == "Elder not found.":
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=400, detail=error)
    return data

@router.get("/{elder_id}", response_model=CareReportListResponse, status_code=200)
def list_care_reports_api(
    elder_id: int,
    type: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    data, error = list_care_reports(
        db=db,
        elder_id=elder_id,
        report_type=type,
        search=search,
        limit=limit,
        offset=offset,
    )

    if error:
        if error == "Elder not found.":
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=400, detail=error)
    
    return data

@router.get("/{elder_id}/{report_id}", response_model=CareReportDetailResponse, status_code=200)
def get_care_report_detail_api(
    elder_id: int,
    report_id: int,
    db: Session = Depends(get_db),
):
    data, error = get_care_report_detail(
        db=db,
        elder_id=elder_id,
        report_id=report_id,
    )

    if error:
        if error == "Elder not found." or error == "Report not found.":
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=400, detail=error)
    
    return data