from pydantic import BaseModel, Field
from typing import List
from datetime import date, datetime


class ElderFormCreate(BaseModel):
    elder_id: int = Field(..., gt=0)

    mood: str
    sleep_quantity: str
    water_intake: str
    appetite_level: str
    energy_level: str
    overall_day: str
    movement_today: str
    loneliness_level: str
    talk_interaction: str
    stress_level: str

    pain_areas: List[str]
    activities: List[str]

    info_date: date


class ElderFormCreateResponse(BaseModel):
    message: str
    check_in_id: int
    elder_id: int
    info_date: date
    recorded_at: datetime


class ElderFormResponse(BaseModel):
    check_in_id: int
    elder_id: int

    mood: str
    sleep_quantity: str
    water_intake: str
    appetite_level: str
    energy_level: str
    overall_day: str
    movement_today: str
    loneliness_level: str
    talk_interaction: str
    stress_level: str

    pain_areas: List[str]
    activities: List[str]

    info_date: date
    recorded_at: datetime