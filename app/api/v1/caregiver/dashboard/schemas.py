from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CaregiverNameResponse(BaseModel):
    caregiver_id: int
    full_name: str

class MissedMedicationCountResponse(BaseModel):
    elder_id: int
    missed_tdy_count: int

class UpcomingAppointmentCountResponse(BaseModel):
    elder_id: int
    upcoming_count: int

class QuickAlertItem(BaseModel):
    title: str
    subtitle: str
    type: str #missed_medicine | missed_checkin | upcoming_appointment

class DashboardHomeResponse(BaseModel):
    elder_id: int
    caregiver_id: int
    caregiver_name: str
    missed_medication_today: int
    upcoming_appointments_7_days: int
    quick_alerts: List[QuickAlertItem] = []
