# app/services/meal_scheduler.py
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.fcm_service import send_push_notification

SERVER_TZ = ZoneInfo("Asia/Colombo")

STATUS_PENDING = 1
STATUS_TAKEN = 2
STATUS_MISSED = 3
STATUS_SKIPPED = 4

MEAL_SLOTS = [
    ("BREAKFAST", 8, 0),
    ("LUNCH", 12, 0),
    ("DINNER", 19, 0),
]

_TZ_OFFSET_RE = re.compile(r"([+-])\s*(\d{2}):(\d{2})")


@dataclass(frozen=True)
class ElderRow:
    elder_id: int
    full_name: str
    tz_text: str
    fcm_token: str


def _parse_offset_minutes(tz_text: str) -> int:
    if not tz_text:
        return 330  # default +05:30
    m = _TZ_OFFSET_RE.search(tz_text)
    if not m:
        return 330
    sign = 1 if m.group(1) == "+" else -1
    hh = int(m.group(2))
    mm = int(m.group(3))
    return sign * (hh * 60 + mm)


def _local_now(server_now: datetime, tz_text: str) -> datetime:
    offset_min = _parse_offset_minutes(tz_text)
    return server_now.astimezone(ZoneInfo("UTC")) + timedelta(minutes=offset_min)


def _meal_message(meal_time: str, name: str) -> tuple[str, str]:
    name = name.strip() or "there"

    if meal_time == "BREAKFAST":
        return (
            "Breakfast Reminder",
            f"Hi {name}, it's breakfast time.\n\nPlease eat your breakfast and log what you ate in the app."
        )
    if meal_time == "LUNCH":
        return (
            "Lunch Reminder",
            f"Hi {name}, it's lunch time.\n\nPlease have your lunch and update the meal status in the app."
        )
    return (
        "Dinner Reminder",
        f"Hi {name}, it's dinner time.\n\nPlease have your dinner and record your diet in the app."
    )


def run_due_meal_reminders(db: Session) -> None:
    server_now = datetime.now(SERVER_TZ).replace(second=0, microsecond=0)

    q = text("""SELECT u.UserID, u.FullName, u.Timezone, ud.FCMToken FROM Users u
        JOIN UserDevices ud
            ON ud.UserID = u.UserID
           AND ud.app_type = 'elder' WHERE u.IsActive = 1
          AND ud.FCMToken IS NOT NULL
          AND LTRIM(RTRIM(ud.FCMToken)) <> ''
          AND ud.LastUpdated = (
              SELECT MAX(ud2.LastUpdated) FROM UserDevices ud2 WHERE ud2.UserID = u.UserID AND ud2.app_type = 'elder')""")

    elders = db.execute(q).fetchall()

    for r in elders:
        elder = ElderRow(
            elder_id=int(r.UserID),
            full_name=str(r.FullName or ""),
            tz_text=str(r.Timezone or ""),
            fcm_token=str(r.FCMToken),
        )

        local_dt = _local_now(server_now, elder.tz_text)
        local_date = local_dt.date()

        for meal_time, hh, mm in MEAL_SLOTS:
            if local_dt.hour != hh or local_dt.minute != mm:
                continue

            # keep your same scheduling logic
            scheduled_for = datetime(
                local_date.year,
                local_date.month,
                local_date.day,
                hh,
                mm,
                tzinfo=SERVER_TZ
            )

            exists = db.execute(
                text("""SELECT 1 FROM MealAdherence WHERE ElderID = :eid
                      AND MealTime = :mt AND ScheduledFor = :sf"""),
                {
                    "eid": elder.elder_id,
                    "mt": meal_time,
                    "sf": scheduled_for
                }
            ).fetchone()

            if not exists:
                db.execute(
                    text("""INSERT INTO MealAdherence (ElderID, MealTime, ScheduledFor, StatusID, UpdatedAt) VALUES
                            (:eid, :mt, :sf, :status_id, GETDATE())"""),
                    {
                        "eid": elder.elder_id,
                        "mt": meal_time,
                        "sf": scheduled_for,
                        "status_id": STATUS_PENDING
                    }
                )

            title, body = _meal_message(meal_time, elder.full_name)

            payload = {
                "type": "MEAL_REMINDER",
                "elderId": str(elder.elder_id),
                "mealTime": meal_time,
                "scheduledFor": scheduled_for.isoformat(),
            }

            try:
                send_push_notification(elder.fcm_token, title, body, payload)
            except Exception:
                pass

    db.commit()


def mark_missed_meals(db: Session) -> None:
    now = datetime.now(SERVER_TZ).replace(tzinfo=None)

    db.execute(
        text("""UPDATE MealAdherence SET StatusID = :missed_status, UpdatedAt = GETDATE() WHERE StatusID = :pending_status
              AND DATEADD(hour, 24, ScheduledFor) <= :now"""),
        {
            "missed_status": STATUS_MISSED,
            "pending_status": STATUS_PENDING,
            "now": now
        }
    )

    db.commit()