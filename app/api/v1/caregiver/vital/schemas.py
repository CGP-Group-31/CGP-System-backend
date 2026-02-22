from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class VitalCreate(BaseModel):
    elder_id: int = Field(..., gt=0)
    vital_type_id: int = Field(..., gt=0)
    value: float = Field(..., gt=-1)
    notes: Optional[str]=Field(None, max_length=255)
    caregiver_id: int = Field(..., gt=0)

class GetVitalTypes(BaseModel):
    VitalTypeID: int
    VitalName: str


class VitalResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    elder_id: int = Field(alias="ElderID")
    vital_type_id: int = Field(alias="VitalTypeID")
    value: float = Field(alias="Value")
    notes: str = Field(alias="Notes")

class VitalUpdate(BaseModel):
    #vital_type_id: int
    value: Optional[float] = Field(None, gt=-1)
    notes: Optional[str]=Field(None, max_length=255)
 
