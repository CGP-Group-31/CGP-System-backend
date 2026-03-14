from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ComplaintCreateRequest(BaseModel):
    complainant_id: int = Field(..., gt=0)
    subject: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class MessageResponse(BaseModel):
    message: str

    class Config:
        populate_by_name = True
        from_attributes = True