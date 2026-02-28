from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class SOSTriggerRequest(BaseModel):
    elder_id: int = Field(..., gt=0)
    relationship_id: int = Field(..., gt=0)
    trigger_type_id: int = Field(..., gt=0)

class SOSTriggerResponse(BaseModel):
    status: str
    sos_id: int
    triggered_at: datetime

