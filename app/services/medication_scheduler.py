# app/services/medication_scheduler.py
from datetime import datetime, date, time as dtime
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services.fcm_service import send_medication_push
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Colombo")


STATUS_PENDING = 1
STATUS_MISSED = 3

def is_due_today(repeat_days: str, start_date: date, today: date) -> bool:
    repeat_days = (repeat_days or "").strip()

    if repeat_days == "Daily":
        return True

    if repeat_days == "EveryOtherDay":
        return (today - start_date).days % 2 == 0

    allowed = {d.strip() for d in repeat_days.split(",") if d.strip()}
    return today.strftime("%a") in allowed


#  Then define the scheduler
def run_due_medication_reminders(db: Session):
    now = datetime.now(TZ)
    today = now.date()

    q = text("""SELECT
            ms.ScheduleID,
            m.ElderID,
            m.MedicationName,
            m.Dosage,
            m.Instructions,
            ms.TimeOfDay,
            ms.RepeatDays,
            ms.StartDate,
            ms.EndDate,
            ud.FCMToken
        FROM MedicationSchedules ms JOIN Medications m ON m.MedicationID = ms.MedicationID
        LEFT JOIN UserDevices ud ON ud.UserID = m.ElderID AND ud.app_type = 'elder' WHERE ms.IsActive = 1 AND m.IsActive = 1""")

    rows = db.execute(q).fetchall()

    for r in rows:
        if not r.FCMToken:
            continue

        if today < r.StartDate:
            continue
        if r.EndDate and today > r.EndDate:
            continue

        if not is_due_today(r.RepeatDays, r.StartDate, today):
            continue

        tod = r.TimeOfDay
        if tod.hour != now.hour or tod.minute != now.minute:
            continue

        scheduled_for = datetime(
            today.year, today.month, today.day,
            tod.hour, tod.minute,
            tzinfo=TZ
        )

        exists = db.execute(text("""SELECT 1 FROM MedicationAdherence
            WHERE ScheduleID = :sid AND ElderID = :eid AND ScheduledFor = :sf"""), {"sid": r.ScheduleID, "eid": r.ElderID, "sf": scheduled_for}).fetchone()

        if exists:
            continue

        db.execute(text("""INSERT INTO MedicationAdherence (ScheduleID, ElderID, StatusID, ScheduledFor)
            VALUES (:sid, :eid, 1, :sf)"""), {"sid": r.ScheduleID, "eid": r.ElderID, "sf": scheduled_for})

        send_medication_push(
            token=r.FCMToken,
            title="Medicine Reminder",
            body=f"{r.MedicationName}",
            data={
                "type": "MED_REMINDER",
                "scheduleId": r.ScheduleID,
                "elderId": r.ElderID,
                "scheduledFor": scheduled_for.isoformat(),
                "medicationName": r.MedicationName,
                "dosage": r.Dosage or "",
                "instructions": r.Instructions or "",
                "durationSec": 60,
            }
        )

    db.commit()

def mark_missed_adherence(db: Session):

    now = datetime.now(TZ)
    now_for_db = now.replace(tzinfo=None)

    q = text("""UPDATE MedicationAdherence
        SET StatusID = :missed_id
        WHERE TakenAt IS NULL
          AND StatusID = :pending_id
          AND DATEADD(hour, 3, ScheduledFor) <= :now""")

    db.execute(q, {
        "missed_id": STATUS_MISSED,
        "pending_id": STATUS_PENDING,
        "now": now_for_db
    })

    db.commit()