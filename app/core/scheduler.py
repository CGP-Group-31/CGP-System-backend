# app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.database import SessionLocal
from app.services.medication_scheduler import ( run_due_medication_reminders, mark_missed_adherence,)
from app.services.appointment_scheduler import run_due_appointment_reminders
from app.services.hydration_scheduler import run_due_hydration_reminders
from app.services.meal_scheduler import run_due_meal_reminders, mark_missed_meals
from app.services.checking_scheduler import run_due_checking_reminders
from app.services.daily_report_scheduler import run_due_daily_reports
import asyncio

scheduler = BackgroundScheduler(timezone="Asia/Colombo")


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(  # working
        func=_medication_job,
        trigger=IntervalTrigger(minutes=1),
        id="medication_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    scheduler.add_job(
        func=_appointment_job,
        trigger=IntervalTrigger(minutes=1),
        id="appointment_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    scheduler.add_job(
        func=_hydration_job,
        trigger=IntervalTrigger(minutes=1),
        id="hydration_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    scheduler.add_job(
        func=_meal_job,
        trigger=IntervalTrigger(minutes=1),
        id="meal_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    scheduler.add_job(
        func=_medication_mark_missed_job,
        trigger=IntervalTrigger(minutes=10),
        id="medication_mark_missed",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    scheduler.add_job(
        func=_meal_mark_missed_job,
        trigger=IntervalTrigger(minutes=60),
        id="meal_mark_missed",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    scheduler.add_job(
        func=_checking_job,
        trigger=IntervalTrigger(minutes=1),
        id="daily_checking_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=30,
    )

    scheduler.add_job(
        func=_daily_report_job,
        trigger=IntervalTrigger(minutes=5),
        id="daily_report_generation",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=120,
    )

    scheduler.start()


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


def _meal_job():
    db = SessionLocal()
    try:
        run_due_meal_reminders(db)
    finally:
        db.close()


def _medication_mark_missed_job():
    db = SessionLocal()
    try:
        mark_missed_adherence(db)
    finally:
        db.close()


def _meal_mark_missed_job():
    db = SessionLocal()
    try:
        mark_missed_meals(db)
    finally:
        db.close()

def _checking_job():
    db = SessionLocal()
    try:
        run_due_checking_reminders(db)
    finally:
        db.close()

def _daily_report_job():
    db = SessionLocal()
    try:
        asyncio.run(run_due_daily_reports(db))
    finally:
        db.close()