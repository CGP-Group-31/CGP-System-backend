from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

class MedicationCreateRequest(BaseModel):
    elderId: int
    caregiverId: int   
    name: str
    dosage: str
    instructions: str
    times: list[str]
    repeatDays: str
    startDate: date
    endDate: Optional[date] = None



class MedicationCreateResponse(BaseModel):
    medicationId: int
    elderId: int
    name: str
    dosage: str
    instructions: str
    times: List[str]
    repeatDays: str
    startDate: date
    endDate: Optional[date]
