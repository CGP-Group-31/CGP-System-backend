from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel


class ElderDayOverview(BaseModel):
    mood: Optional[str] = None
    sleep_quantity: Optional[str] = None
    water_intake: Optional[str] = None
    appetite_level: Optional[str] = None
    energy_level: Optional[str] = None
    overall_day: Optional[str] = None
    movement_today: Optional[str] = None
    loneliness_level: Optional[str] = None
    talk_interaction: Optional[str] = None
    stress_level: Optional[str] = None

class PainReport(BaseModel):
    pain_areas: List[str] = []

class MedicationAdherenceSection(BaseModel):
    taken_count: int = 0
    missed_count: int = 0
    missed_items: List[str] = []

class MealAdherenceSection(BaseModel):
    breakfast: Optional[str] = None
    lunch: Optional[str] = None
    dinner: Optional[str] = None


class CareReportItem(BaseModel):
    report_id: int
    elder_id: int
    report_type: Literal["daily", "weekly"]
    title: str
    period_start: date
    period_end: date
    generated_at: datetime


class CareReportListResponse(BaseModel):
    reports: List[CareReportItem]
    total: int

class CareReportDetailResponse(BaseModel):
    report_id: int
    elder_id: int
    report_type: Literal["daily", "weekly"]
    title: str
    period_start: date
    period_end: date
    report_text: str
    generated_at: datetime

    elder_day_overview: Optional[ElderDayOverview] = None
    pain_report: Optional[PainReport] = None
    activities: List[str] = []
    ai_checkin_insights: Optional[str] = None
    medication_adherence: MedicationAdherenceSection
    meal_adherence: MealAdherenceSection
    concerns: List[str] = []
    caregiver_recommendation: Optional[str] = None