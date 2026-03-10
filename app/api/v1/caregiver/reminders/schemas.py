from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class TodayMedsResponse(BaseModel):
    adherence_id: int = Field(..., alias="AdherenceID")
    elder_id: int = Field(..., alias="ElderID")
    schedule_id: int = Field(..., alias="ScheduleID")
    medication_id: int = Field(..., alias="MedicationID")
    medication_name: str = Field(..., alias="MedicationName")
    dosage: Optional[str] = Field(None, alias="Dosage")
    scheduled_for: datetime = Field(..., alias="ScheduledFor")
    taken_at: Optional[datetime] = Field(None, alias="TakenAt")
    status_id: int = Field(..., alias="StatusID")


class TodayMedSummaryResponse(BaseModel):
    pending: List[TodayMedsResponse] = []
    taken: List[TodayMedsResponse] = []
    missed: List[TodayMedsResponse] = []