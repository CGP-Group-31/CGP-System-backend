# app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.database import SessionLocal
from app.services.medication_scheduler import run_due_medication_reminders, mark_missed_adherence
from app.services.appointment_scheduler import run_due_appointment_reminders
from app.services.hydration_scheduler import run_due_hydration_reminders 
from app.services.meal_scheduler import run_due_meal_reminders, mark_missed_meals

scheduler = BackgroundScheduler(timezone="Asia/Colombo")


def start_scheduler():
    scheduler.add_job(
        func=_medication_job,
        trigger=IntervalTrigger(minutes=10),
        id="medication_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    # Appointment reminders 
    scheduler.add_job(
        func=_appointment_job,
        trigger=IntervalTrigger(minutes=10),
        id="appointment_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    scheduler.add_job(
        func=_hydration_job,
        trigger=IntervalTrigger(minutes=10),
        id="hydration_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    scheduler.add_job(
        func=meal_reminder_job,
        trigger=IntervalTrigger(minutes=10),
        id="meal_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )
    scheduler.add_job(
        job_mark_missed,
        trigger=IntervalTrigger(minutes=10),
        id="medication_mark_missed",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60
    )
    
    scheduler.add_job(
        meal_missed_job,
        trigger=IntervalTrigger(minutes=360),
        id="meal_mark_missed",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60
    )
    scheduler.start()
    # scheduler.add_job(meal_reminder_job, "interval", minutes=1, id="meal_reminders", replace_existing=True)
    # scheduler.add_job(meal_missed_job, "interval", minutes=5, id="meal_missed", replace_existing=True)
def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
def _medication_job():
    db = SessionLocal()
    try:
        run_due_medication_reminders(db)
    finally:
        db.close()


def _appointment_job():
    db = SessionLocal()
    try:
        run_due_appointment_reminders(db)
    finally:
        db.close()

def _hydration_job():
    db = SessionLocal()
    try:
        run_due_hydration_reminders(db)
    finally:
        db.close()

# def _meal_job():
#     db = SessionLocal()
#     try:
#         run_due_meal_reminders(db)
#     finally:
#         db.close()

def job_mark_missed():
    db = SessionLocal()
    try:
        mark_missed_adherence(db)
    finally:
        db.close()

def meal_reminder_job():
    db = SessionLocal()
    try:
        run_due_meal_reminders(db)
    finally:
        db.close()


def meal_missed_job():
    db = SessionLocal()
    try:
        mark_missed_meals(db)
    finally:
        db.close()
