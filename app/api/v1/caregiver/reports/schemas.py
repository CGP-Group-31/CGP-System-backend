from datetime import date, datetime
from typing import List, Literal
from pydantic import BaseModel


class CareReportItem(BaseModel):
    report_id: int
    elder_id: int
    report_type: Literal["daily", "weekly"]
    period_start: date
    period_end: date
    report_text: str
    generated_at: datetime


class CareReportListResponse(BaseModel):
    reports: List[CareReportItem]