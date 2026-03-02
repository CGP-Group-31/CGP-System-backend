from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class VitalTypeItem(BaseModel):
    vital_type_id: int
    vital_name: str
    unit: Optional[str] = None

class VitalTypesResponse(BaseModel):
    status: str = "ok"
    types: List[VitalTypeItem]

class VitalCreate(BaseModel):
    elder_id: int = Field(..., gt=0)
    vital_type_id: int = Field(..., gt=0)
    value: float = Field(..., gt=0)  
    notes: Optional[str] = None
    recorded_by: int = Field(..., gt=0)  


class VitalCreateResponse(BaseModel):
    status: str = "ok"
    record_id: int
    recorded_at: datetime

class VitalRecordItem(BaseModel):
    record_id: int
    elder_id: int
    vital_type_id: int
    vital_name: str
    unit: Optional[str] = None
    value: float
    notes: Optional[str] = None
    recorded_by: int
    recorded_at: datetime

class VitalCategoryLatest(BaseModel):
    vital_type_id: int
    vital_name: str
    unit: Optional[str] = None
    last: List[VitalRecordItem]

class ElderVitalsLatestResponse(BaseModel):
    status: str = "ok"
    elder_id: int
    limit_per_type: int
    categories: List[VitalCategoryLatest]