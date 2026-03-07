from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class UpdateMealStatusRequest(BaseModel):
    elderId: int = Field(..., gt=0)
    mealTime: str
    scheduledFor: datetime
    statusId: int
    diet: Optional[str] = None

    @field_validator("mealTime")
    @classmethod
    def validate_meal_time(cls, v: str) -> str:
        meal = v.strip().upper()
        if meal not in ("BREAKFAST", "LUNCH", "DINNER"):
            raise ValueError("mealTime must be BREAKFAST, LUNCH, or DINNER")
        return meal

    @field_validator("statusId")
    @classmethod
    def validate_status_id(cls, v: int) -> int:
        if v not in (2, 3, 4):  # Taken, Missed, Skipped
            raise ValueError("statusId must be 2 (Taken), 3 (Missed), or 4 (Skipped)")
        return v


class MealItemResponse(BaseModel):
    MealAdherenceID: int
    ElderID: int
    MealTime: str
    ScheduledFor: datetime
    StatusID: int
    Diet: Optional[str] = None
    UpdatedAt: datetime


class TodayMealsResponse(BaseModel):
    items: List[MealItemResponse]


class MessageResponse(BaseModel):
    message: str