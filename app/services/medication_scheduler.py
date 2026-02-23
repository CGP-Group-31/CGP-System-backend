# app/services/medication_scheduler.py
from datetime import datetime, date, time as dtime
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services.fcm_service import send_medication_push
from zoneinfo import ZoneInfo
def is_due_today(repeat_days: str, start_date: date, today: date) -> bool:
    repeat_days = (repeat_days or "").strip()
    if repeat_days == "Daily":
        return True
    if repeat_days == "EveryOtherDay":
        return (today - start_date).days % 2 == 0
    allowed = {d.strip() for d in repeat_days.split(",") if d.strip()}
    return today.strftime("%a") in allowed  # Mon Tue Wed...

def run_due_medication_reminders(db: Session):
    # now = datetime.now()
    # today = now.date()
    now = datetime.now(ZoneInfo("Asia/Colombo"))
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
        FROM MedicationSchedules ms
        JOIN Medications m ON m.MedicationID = ms.MedicationID
        LEFT JOIN UserDevices ud
            ON ud.UserID = m.ElderID AND ud.app_type = 'elder'
        WHERE ms.IsActive = 1 AND m.IsActive = 1""")

    rows = db.execute(q).fetchall()

    for r in rows:
        if not r.FCMToken:
            continue

        # date range
        if today < r.StartDate:
            continue
        if r.EndDate is not None and today > r.EndDate:
            continue

        # repeat
        if not is_due_today(r.RepeatDays, r.StartDate, today):
            continue

        # time match
        tod = r.TimeOfDay
        if tod.hour != now.hour or tod.minute != now.minute:
            continue

        scheduled_for = datetime.combine(today, dtime(tod.hour, tod.minute))

        # guard: already inserted for this exact scheduled_for?
        exists = db.execute(text("""SELECT 1 FROM MedicationAdherence
            WHERE ScheduleID = :sid AND ElderID = :eid AND ScheduledFor = :sf
        """), {"sid": r.ScheduleID, "eid": r.ElderID, "sf": scheduled_for}).fetchone()

        if exists:
            continue

        # insert pending
        db.execute(text("""INSERT INTO MedicationAdherence (ScheduleID, ElderID, StatusID, ScheduledFor)
            VALUES (:sid, :eid, 1, :sf)"""), {"sid": r.ScheduleID, "eid": r.ElderID, "sf": scheduled_for})

        title = "Medicine Reminder"
        body = f"{r.MedicationName}\nDosage: {r.Dosage or '-'}\n{r.Instructions or ''}".strip()

        send_medication_push(
            token=r.FCMToken,
            title=title,
            body=body,
            data={
                "type": "MED_REMINDER",
                "scheduleId": r.ScheduleID,
                "elderId": r.ElderID,
                "scheduledFor": scheduled_for.isoformat()
            }
        )

    db.commit()