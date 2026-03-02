from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime


class LocationShareRequest(BaseModel):
    elder_id: int = Field(..., gt=0)
    latitude: float
    longitude: float
    

    