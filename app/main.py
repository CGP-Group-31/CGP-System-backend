from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import register_exception_handlers


from app.api.v1.caregiver.auth.routes import router as caregiver_auth
from app.core.exceptions import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)
from app.api.v1.caregiver.createelder.routes import router as caregiver_create_elder
from app.api.v1.caregiver.medication.routes import router as caregiver_medication

# from app.api.v1.elder.auth.routes import router as elder_auth
# from app.api.v1.caregiver.profile.routes import router as caregiver_profile
# from app.api.v1.caretaker.auth.routes import router as caretaker_auth





app = FastAPI(
    title="Elder Care Backend",
    version="1.0.0"
)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
register_exception_handlers(app)

app.include_router(caregiver_create_elder, prefix="/api/v1/caregiver", tags=["Caregiver"])



app.include_router(caregiver_auth, prefix="/api/v1/caregiver", tags=["Caregiver"])

app.include_router(caregiver_medication, prefix="/api/v1/caregiver", tags=["Medication"])
# app.include_router(elder_auth, prefix="/api/v1/elder", tags=["Elder"])
# app.include_router(caregiver_profile, prefix="/api/v1/caregiver", tags=["Caregiver"])
# app.include_router(caretaker_auth, prefix="/api/v1/caretaker", tags=["Caretaker"])






@app.get("/health")
def health():
    return {"status": "ok"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)