from pydantic import BaseModel, Field
from datetime import datetime

class SOSLogResponse(BaseModel):
    sos_id: int = Field(alias="SOSID")
    elder_id: int = Field(alias="ElderID")
    triggered_at: datetime = Field(alias="TriggeredAt")

class SOSLogHistoryResponse(BaseModel):
    sos_id: int = Field(alias="SOSID")
    elder_id: int = Field(alias="ElderID")
    triggered_at: datetime = Field(alias="TriggeredAt")