from pydantic import BaseModel
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
