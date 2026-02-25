# app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.database import SessionLocal
from app.services.medication_scheduler import run_due_medication_reminders

scheduler = BackgroundScheduler(timezone="Asia/Colombo")


def start_scheduler():
    
    scheduler.add_job(
        func=_medication_job,
        trigger=IntervalTrigger(minutes=1),
        id="medication_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )
    scheduler.start()


def _medication_job():
    db = SessionLocal()
    try:
        run_due_medication_reminders(db)
    finally:
        db.close()