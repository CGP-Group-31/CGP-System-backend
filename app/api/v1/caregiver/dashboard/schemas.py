from pydantic import BaseModel
from datetime import datetime

class CaregiverNameResponse(BaseModel):
    elder_id: int
    full_name: str

class MissedMedicationCountResponse(BaseModel):
    elder_id: int
    full_name: str

class UpcomingAppointmentCountResponse(BaseModel):
    elder_id: int
    upcoming_count: int

class LocationResponse(BaseModel):
    elder_id: int
    location: dict