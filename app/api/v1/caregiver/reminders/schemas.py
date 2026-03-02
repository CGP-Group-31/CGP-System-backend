from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional,List

class TodayMedsResponse(BaseModel):
    adherence_id: int = Field(..., alias="AdherenceID")
    elder_id: int = Field(...,alias="ElderID")
    schedule_id: int = Field(...,alias="ScheduleID")
    medication_id: int = Field(...,alias="MedicationID")
    medication_name: int = Field(alias="MedicationName")
    dosage: int = Field(alias="Dosage")
    scheduled_for: int = Field(alias="ScheduledFor")
    status_id: int = Field(alias="StatusID")


#if we use one api for all 3..
class TodayMedSummaryResponse(BaseModel):
    elder_id: int = Field(alias="ElderID")
    elder_id:List[TodayMedsResponse] = []
    elder_id: List[TodayMedsResponse] = []
    elder_id: List[TodayMedsResponse] = []
   