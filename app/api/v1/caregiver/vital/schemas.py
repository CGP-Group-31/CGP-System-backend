from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class VitalCreate(BaseModel):
    elder_id: int
    vital_type_id: int
    value1: float
    value2: Optional[float]=None
   #remove notes
    notes: Optional[str]=Field(None, max_length=255)
    recorded_by: int


class VitalResponse(BaseModel):
    message: str
    recorded_ids: list[int]
