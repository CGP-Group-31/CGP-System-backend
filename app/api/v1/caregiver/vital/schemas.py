from pydantic import BaseModel, Field, ConfigDict, RootModel
from typing import Optional, Dict, List
from datetime import datetime

class VitalCreate(BaseModel):
    elder_id: int = Field(..., gt=0)
    vital_type_id: int = Field(..., gt=0)
    value: float = Field(..., gt=-1)
    notes: Optional[str]=Field(None, max_length=255)
    caregiver_id: int = Field(..., gt=0)

class VitalTypeResponse(BaseModel):
    VitalTypeID: int
    VitalName: str
    Unit: str

class GetVital(BaseModel):
    data: List[VitalTypeResponse]


class VitalResponse(BaseModel):
    record_id: int 
    vital_type_id: int
    value: float
    unit: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: datetime

class VitalLAtestResponse(RootModel[Dict[str, Optional[VitalResponse]]]):
    pass


 
