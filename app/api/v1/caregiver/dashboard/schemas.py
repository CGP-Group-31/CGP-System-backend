from pydantic import BaseModel
from datetime import datetime

class CaregiverNameResponse(BaseModel):
    caregiver_id: int
    full_name: str

class MissedMedicationCountResponse(BaseModel):
    elder_id: int
    missed_tdy_count: int

class UpcomingAppointmentCountResponse(BaseModel):
    elder_id: int
    upcoming_count: int

