# app/services/hydration_scheduler.py
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.fcm_service import send_push_notification

SERVER_TZ = ZoneInfo("Asia/Colombo")

# Hydration slots in user's LOCAL time
HYDRATION_SLOTS = [
    (9, 0),   # 09:00
    (15, 0),  # 15:00
    (20, 0),  # 20:00
]


# "IST +05:30"
# "+05:30"

_TZ_OFFSET_RE = re.compile(r"([+-])\s*(\d{2}):(\d{2})")


@dataclass(frozen=True)
class UserDeviceRow:
    user_id: int
    full_name: str
    tz_text: str
    fcm_token: str


def _parse_timezone_offset_minutes(tz_text: str) -> int:
    if not tz_text:
        return 330

    m = _TZ_OFFSET_RE.search(tz_text)
    if not m:
        return 330

    sign = 1 if m.group(1) == "+" else -1
    hh = int(m.group(2))
    mm = int(m.group(3))

    return sign * (hh * 60 + mm)


def _user_local_now(server_now: datetime, tz_text: str) -> datetime:
    """
    Convert server time to user's local time using offset."""
    offset_min = _parse_timezone_offset_minutes(tz_text)
    return server_now.astimezone(ZoneInfo("UTC")) + timedelta(minutes=offset_min)


def _hydration_message_for_hour(hour: int) -> tuple[str, str]:
    if hour == 9:
        return (
            "Hydration Reminder",
            "Good morning! Please drink a glass of water now. Staying hydrated keeps you strong."
        )

    if hour == 15:
        return (
            "Time to Drink Water",
            "It’s afternoon. Please take a few sips of water now. Your body will thank you."
        )

    return (
        "Evening Hydration",
        "Good evening! Drink some water before you rest. Hydration helps your health."
    )


def run_due_hydration_reminders(db: Session) -> None:
    server_now = datetime.now(SERVER_TZ).replace(second=0, microsecond=0)

    q = text("""
        SELECT
            u.UserID,
            u.FullName,
            u.Timezone,
            ud.FCMToken
        FROM Users u
        JOIN UserDevices ud
          ON ud.UserID = u.UserID
         AND ud.app_type = 'elder'
        WHERE u.IsActive = 1
          AND ud.FCMToken IS NOT NULL
          AND LTRIM(RTRIM(ud.FCMToken)) <> ''
          AND ud.LastUpdated = (
                SELECT MAX(ud2.LastUpdated)
                FROM UserDevices ud2
                WHERE ud2.UserID = u.UserID
                  AND ud2.app_type = 'elder'
          );
    """)

    rows = db.execute(q).fetchall()

    for r in rows:
        user = UserDeviceRow(
            user_id=int(r.UserID),
            full_name=str(r.FullName or "").strip(),
            tz_text=str(r.Timezone or "").strip(),
            fcm_token=str(r.FCMToken),
        )

        local_now = _user_local_now(server_now, user.tz_text)

        for hh, mm in HYDRATION_SLOTS:
            if local_now.hour == hh and local_now.minute == mm:
                title, body = _hydration_message_for_hour(hh)

                data_payload = {
                    "type": "HYDRATION_REMINDER",
                    "userId": str(user.user_id),
                    "localTime": local_now.strftime("%H:%M"),
                    "localDate": local_now.date().isoformat(),
                }

                try:
                    send_push_notification(
                        token=user.fcm_token,
                        title=title,
                        body=body,
                        data=data_payload,
                    )
                except Exception as e:
                    print(f"Hydration reminder send failed for user {user.user_id}: {e}")

                break