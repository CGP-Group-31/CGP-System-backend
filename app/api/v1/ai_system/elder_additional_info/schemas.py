from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class AdditionalInfoItem(BaseModel):
    additional_info_id: int = Field(..., gt=0)
    elder_id: int = Field(..., gt=0)
    caregiver_id: int = Field(..., gt=0)
    cognitive_behavior_notes: Optional[str] = Field(None, max_length=200)
    preferences: Optional[str] = Field(None, max_length=200)
    social_emotional_behavior_notes: Optional[str] = Field(None, max_length=200)
    health_goals: Optional[str] = Field(None, max_length=200)
    special_notes_observations: Optional[str] = Field(None, max_length=200)
    phone_date: date
    week_number: int
    recorded_at: datetime

class AdditionalInfoListResponse(BaseModel):
    status: str = "ok"
    elder_id: int
    items: List[AdditionalInfoItem]
