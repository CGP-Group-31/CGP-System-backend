from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import date, time, datetime
import re

class MedicationItem(BaseModel):
    medication_name: str
    dosage: str | None
    scheduled_for: datetime
    status: str

class MedicationReportResponse(BaseModel):
    elder_id: int
    date: date
    items: list[MedicationItem]

class MealItem(BaseModel):
    meal_time: str
    status: str

class MealReportResponse(BaseModel):
    elder_id: int
    date: date

    breakfast: str
    lunch: str
    dinner: str

    items: list[MealItem]