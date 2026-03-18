from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from .repository import (
    get_additional_info_by_elder,
    get_additional_info_by_elder_month_week,
)
from .schemas import AdditionalInfoListResponse

router = APIRouter(prefix="/additional-info", tags=["AI System"])


def _format_items(rows):
    return [
        {
            "additional_info_id": row["AdditionalInfoID"],
            "elder_id": row["ElderID"],
            "caregiver_id": row["CaregiverID"],
            "cognitive_behavior_notes": row["CognitiveBehaviorNotes"],
            "preferences": row["Preferences"],
            "social_emotional_behavior_notes": row["SocialEmotionalBehaviorNotes"],
            "health_goals": row["HealthGoals"],
            "special_notes_observations": row["SpecialNotesObservations"],
            "phone_date": row["InfoDate"],
            "week_number": row["WeekNumber"],
            "recorded_at": row["RecordedAt"],
        }
        for row in rows
    ]


@router.get("/elder/{elder_id}", response_model=AdditionalInfoListResponse)
def get_additional_info_for_elder(
    elder_id: int,
    db: Session = Depends(get_db),
):
    try:
        rows = get_additional_info_by_elder(db, elder_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ok",
        "elder_id": elder_id,
        "items": _format_items(rows),
    }


@router.get("/elder/{elder_id}/by-month", response_model=AdditionalInfoListResponse)
def get_additional_info_for_elder_by_month(
    elder_id: int,
    year_month: str = Query(
        ...,
        description="Filter by year-month in YYYY-MM format",
        pattern=r"^\d{4}-\d{2}$",
        examples=["2026-03"],
    ),
    db: Session = Depends(get_db),
):
    year, month = year_month.split("-")
    year = int(year)
    month = int(month)
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Invalid year_month format")

    today = date.today()
    current_week_number = (today.day + 6) // 7
    target_week = current_week_number - 1
    if target_week < 1:
        return {
            "status": "ok",
            "elder_id": elder_id,
            "items": [],
        }

    try:
        rows = get_additional_info_by_elder_month_week(db, elder_id, year, month, target_week)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


    rows = [row for row in rows if row.get("WeekNumber") == target_week]

    return {
        "status": "ok",
        "elder_id": elder_id,
        "items": _format_items(rows),
    }
