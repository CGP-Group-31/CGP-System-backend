from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional, List

class VitalRecordItem(BaseModel):
    record_id: int
    elder_id: int
    vital_name: str
    unit: Optional[str] = None
    value: float
    notes: Optional[str] = None
    recorded_at: datetime

class ElderVitalsLastWeekResponse(BaseModel):
    status: str = "ok"
    elder_id: int
    week_start_date: date
    week_end_date: date
    records: List[VitalRecordItem]

class DailyReportItem(BaseModel):
    report_id: Optional[int] = None   
    report_date: date
    # report_text: Optional[str] = None
    report_json: Optional[str] = None
    generated_at: Optional[datetime] = None


class WeeklyDailyReportsResponse(BaseModel):
    week_start: date
    week_end: date
    reports: List[DailyReportItem]


class SOSLogItem(BaseModel):
    sos_id: int
    trigger_type: str = Field(..., min_length=10, max_length=16)
    triggered_at: str

class SOSWeeklyResponse(BaseModel):
    week_start: date
    week_end: date
    sos_logs: List[SOSLogItem]