from fastapi import FastAPI
from app.api.v1 import auth, users, messaging
from app.core.scheduler import start_scheduler

app = FastAPI(title="Elder Care Backend")

app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(messaging.router, prefix="/api/v1/messages")

@app.on_event("startup")
def startup():
    start_scheduler()

@app.get("/")
def root():
    return {"status": "ok"}
