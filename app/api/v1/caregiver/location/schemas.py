from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime

class LocationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    location_id: int = Field(alias="LocationID")
    elder_id: int = Field(alias="ElderID")
    latitude: float = Field(alias="Latitude")
    longitude: float = Field(alias="Longitude")
    recorded_at: datetime = Field(alias="RecordedBy")

class LocationLatestResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    elder_id: int = Field(alias="ElderID")
    location: LocationResponse

class LocationHistoryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    elder_id: int = Field(alias="ElderID")
    history: List[LocationResponse]