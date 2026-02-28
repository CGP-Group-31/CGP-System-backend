# app/services/hydration_scheduler.py
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
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

# Persistent "already sent" cache (no DB)
CACHE_FILE = Path(__file__).resolve().parent / "hydration_sent_cache.json"

# Parse strings like:
# "IST +05:30"
# "+05:30"
# "UTC+05:30"
# "GMT +05:30"
_TZ_OFFSET_RE = re.compile(r"([+-])\s*(\d{2}):(\d{2})")


@dataclass(frozen=True)
class UserDeviceRow:
    user_id: int
    full_name: str
    tz_text: str
    fcm_token: str


def _load_cache() -> dict:
    """
    Cache structure:
    {
      "sent": {
         "userId|YYYY-MM-DD|HH:MM": true,
         ...
      },
      "last_cleanup": "YYYY-MM-DD"
    }
    """
    if not CACHE_FILE.exists():
        return {"sent": {}, "last_cleanup": ""}

    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"sent": {}, "last_cleanup": ""}
        data.setdefault("sent", {})
        data.setdefault("last_cleanup", "")
        if not isinstance(data["sent"], dict):
            data["sent"] = {}
        return data
    except Exception:
        return {"sent": {}, "last_cleanup": ""}


def _save_cache(cache: dict) -> None:
    try:
        CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    except Exception:
        # Don't crash scheduler if disk write fails
        pass


def _cleanup_cache_daily(cache: dict, today_server: str) -> None:
    """
    Remove entries older than 3 days to keep file small.
    """
    if cache.get("last_cleanup") == today_server:
        return

    sent = cache.get("sent", {})
    cutoff_date = (datetime.now(SERVER_TZ).date() - timedelta(days=3)).isoformat()

    # key format: "userId|YYYY-MM-DD|HH:MM"
    new_sent = {}
    for k, v in sent.items():
        try:
            parts = k.split("|")
            if len(parts) != 3:
                continue
            date_part = parts[1]
            if date_part >= cutoff_date:
                new_sent[k] = v
        except Exception:
            continue

    cache["sent"] = new_sent
    cache["last_cleanup"] = today_server


def _parse_timezone_offset_minutes(tz_text: str) -> int:
    """
    Extract offset minutes from a string like "IST +05:30".
    If not found, default to Asia/Colombo (UTC+05:30) -> +330 minutes.
    """
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
    Convert server_now (timezone-aware) to user's local time using offset minutes.
    We only have offset, not IANA zone, but enough for fixed-offset schedules.
    """
    offset_min = _parse_timezone_offset_minutes(tz_text)
    return server_now.astimezone(ZoneInfo("UTC")) + timedelta(minutes=offset_min)


def _slot_key(user_id: int, local_dt: datetime) -> str:
    """
    Identify this alert uniquely per user per day per slot-minute.
    """
    return f"{user_id}|{local_dt.date().isoformat()}|{local_dt.strftime('%H:%M')}"


def _hydration_message_for_hour(hour: int) -> tuple[str, str]:
    """
    Elder-friendly messages.
    """
    if hour == 9:
        return (
            "Hydration Reminder ",
            "Good morning! Please drink a glass of water now. Staying hydrated keeps you strong."
        )
    if hour == 15:
        return (
            "Time to Drink Water ",
            "It’s afternoon. Please take a few sips of water now. Your body will thank you."
        )
    # 20:00
    return (
        "Evening Hydration ",
        "Good evening! Drink some water before you rest. Hydration helps your health."
    )


def run_due_hydration_reminders(db: Session) -> None:
  
    server_now = datetime.now(SERVER_TZ).replace(second=0, microsecond=0)

    cache = _load_cache()
    _cleanup_cache_daily(cache, today_server=server_now.date().isoformat())
    sent_map: dict = cache["sent"]

    # Get elders + latest token (elder app)
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

        # Must match exact minute
        for (hh, mm) in HYDRATION_SLOTS:
            if local_now.hour == hh and local_now.minute == mm:
                key = _slot_key(user.user_id, local_now)

                # Already sent this slot today -> skip
                if sent_map.get(key):
                    break

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
                    sent_map[key] = True
                except Exception:
                    # If send fails, do NOT mark sent (so it can try again next minute)
                    # But since it only matches exact minute, it will only retry within that same minute.
                    pass

                break  # don't check other slots

    cache["sent"] = sent_map
    _save_cache(cache)