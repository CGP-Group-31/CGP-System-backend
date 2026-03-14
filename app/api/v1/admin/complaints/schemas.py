from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ComplaintResponse(BaseModel):
    complaint_id: int
    complainant_id: int
    subject: str
    description: str
    status: Optional[str] = None
    created_at: Optional[datetime] = None