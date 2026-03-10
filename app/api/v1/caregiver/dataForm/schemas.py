from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import date, datetime
import re


class AdditionalInfoCreate(BaseModel):
    elder_id: int = Field(...,gt=0)
    caregiver_id: int = Field(...,gt=0)
    cognitive_behavior_notes: Optional[str] = Field(None)
    preferences: Optional[str] = Field(None)
    social_emotional_behavior_notes: Optional[str] = Field(None)
    health_goals: Optional[str] = None
    special_notes_observations: Optional[str] = None
    phone_date: date = Field(...)

class AdditionalInfoCreateResponse(BaseModel):
    message: str
    additional_info_id: int
    week_number: int
    recorded_at: datetime   


class AdditionalInfoResponse(BaseModel):
    additional_info_id: int = Field(...,gt=0)
    elder_id: int = Field(...,gt=0)
    caregiver_id: int = Field(...,gt=0)
    cognitive_behavior_notes: Optional[str] = Field(None)
    preferences: Optional[str] = Field(None)
    social_emotional_behavior_notes: Optional[str] = Field(None)
    health_goals: Optional[str] = None
    special_notes_observations: Optional[str] = None
    phone_date: date 
    week_number: int 
    recorded_at: datetime


    




    