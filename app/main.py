from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import register_exception_handlers

from contextlib import asynccontextmanager
import os

from app.core.exceptions import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)
import app.modules.notifications.router
from app.core.scheduler import start_scheduler
from app.modules.notifications.router import router as notifications_router
from app.messaging.routes import router as messaging_router


#caregiver routes
from app.api.v1.caregiver.auth.routes import router as caregiver_auth
from app.api.v1.caregiver.createelder.routes import router as caregiver_create_elder
from app.api.v1.caregiver.medication.routes import router as caregiver_medication
from app.api.v1.caregiver.appointments.routes import router as caregiver_appointment_mgt
from app.api.v1.caregiver.caregiverProfile.routes import router as caregiver_profile
from app.api.v1.caregiver.elderManage.routes import router as caregiver_elder_mgt
from app.api.v1.caregiver.dashboard.routes import router as caregiver_dashboard
from app.api.v1.caregiver.location.routes import router as caregiver_location
from app.api.v1.caregiver.vital.routes import router as caregiver_vital_mgt
from app.api.v1.caregiver.reminders.routes import router as caregiver_reminder


#elder routes
from app.api.v1.elder.medication_adherence.routes import router as elder_medication
from app.api.v1.elder.location.routes import router as elder_location
from app.modules.notifications.router import router as notifications_router
from app.api.v1.elder.elderProfile.routes import router as elder_profile
from app.api.v1.elder.auth.routes import router as elder_auth
from app.api.v1.elder.meals.routes import router as elder_meals
from app.api.v1.elder.sos.routes import router as sos_router
from app.api.v1.elder.medication_adherence.routes import router as elder_medication
# from app.api.v1.caregiver.profile.routes import router as caregiver_profile
# from app.api.v1.caretaker.auth.routes import router as caretaker_auth



app = FastAPI(
    title="Elder Care Backend",
    version="1.0.0"
)
@app.on_event("startup")
def on_startup():
    start_scheduler()
    
register_exception_handlers(app)


#caregiver
app.include_router(caregiver_create_elder, prefix="/api/v1/caregiver")
app.include_router(caregiver_auth, prefix="/api/v1/caregiver")
app.include_router(caregiver_profile, prefix="/api/v1/caregiver")
app.include_router(caregiver_elder_mgt, prefix="/api/v1/caregiver")
app.include_router(caregiver_medication, prefix="/api/v1/caregiver")
app.include_router(caregiver_appointment_mgt, prefix="/api/v1/caregiver")
app.include_router(caregiver_vital_mgt, prefix="/api/v1/caregiver")
app.include_router(caregiver_dashboard, prefix="/api/v1/caregiver")
app.include_router(caregiver_location, prefix="/api/v1/caregiver")
app.include_router(caregiver_reminder, prefix="/api/v1/caregiver")


#elder routes
app.include_router(elder_auth, prefix="/api/v1/elder")
app.include_router(elder_location, prefix="/api/v1/elder")
app.include_router(elder_medication, prefix="/api/v1/elder")
app.include_router(elder_profile, prefix="/api/v1/elder")
app.include_router(elder_meals, prefix="/api/v1/elder")
app.include_router(sos_router, prefix="/api/v1/elder")
app.include_router(elder_medication, prefix="/api/v1/elder")

app.include_router(notifications_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")

# app.include_router(caregiver_profile, prefix="/api/v1/caregiver", tags=["Caregiver"])
# app.include_router(caretaker_auth, prefix="/api/v1/caretaker", tags=["Caretaker"])




app.include_router(messaging_router)
@app.get("/health")
def health():
    return {"status": "ok"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
