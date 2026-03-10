from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import AdditionalInfoCreate, AdditionalInfoResponse, AdditionalInfoCreateResponse
from .repository import insert_additional_elder_info, get_last_2_info
from typing import List

router= APIRouter(prefix="/additional-info", tags=["Additional Information"])

@router.post("/", response_model=AdditionalInfoCreateResponse)
def create_info(data: AdditionalInfoCreate, db: Session = Depends(get_db)):
    try:
        row = insert_additional_elder_info(db, data)
        db.commit()
        return {
                "message": "Additional info saved successfully",
                "additional_info_id": row["AdditionalInfoID"],
                "phone_date": row["InfoDate"],
                "week_number": row["WeekNumber"],
                "recorded_at": row["RecordedAt"],
            }

    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/elder/{elder_id}/latest-2", response_model=list[AdditionalInfoResponse])
def fetch_latest_info(elder_id: int, db: Session = Depends(get_db)):
    try:
        rows = get_last_2_info(db, elder_id)

        if not rows:
            raise HTTPException(status_code=404, detail="No additional info found")

        return [{
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

    except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    


