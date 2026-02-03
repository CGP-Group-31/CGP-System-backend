from fastapi import FastAPI
from app.api.v1.caregiver.auth.routes import router as caregiver_auth
# from app.api.v1.caregiver.profile.routes import router as caregiver_profile
# from app.api.v1.caretaker.auth.routes import router as caretaker_auth

app = FastAPI(
    title="Elder Care Backend",
    version="1.0.0"
)

app.include_router(caregiver_auth, prefix="/api/v1/caregiver", tags=["Caregiver"])
# app.include_router(caregiver_profile, prefix="/api/v1/caregiver", tags=["Caregiver"])
# app.include_router(caretaker_auth, prefix="/api/v1/caretaker", tags=["Caretaker"])



@app.get("/")
def health_check():
    return {"status": "ok"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)