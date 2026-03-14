import re
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings

# Parse strings like:
# "IST +05:30"
# "+05:30"
# "UTC+05:30"
# "GMT +05:30"
_TZ_OFFSET_RE = re.compile(r"([+-])\s*(\d{2}):(\d{2})")


@dataclass
class ScheduleRow:
    schedule_id: int
    elder_id: int
    schedule_name: str
    local_time: str
    timezone_text: str


def parse_offset_minutes(tz_text: str) -> int:
    if not tz_text:
        return 0

    match = _TZ_OFFSET_RE.search(tz_text)
    if not match:
        return 0

    sign = 1 if match.group(1) == "+" else -1
    hh = int(match.group(2))
    mm = int(match.group(3))

    return sign * (hh * 60 + mm)


def utc_now() -> datetime:
    return datetime.utcnow()


def local_now_for_offset(offset_minutes: int) -> datetime:
    return utc_now() + timedelta(minutes=offset_minutes)


def build_planned_at_utc(local_dt: datetime, offset_minutes: int) -> datetime:
    return local_dt - timedelta(minutes=offset_minutes)


def get_active_schedules(db: Session) -> list[ScheduleRow]:
    q = text("""
        SELECT
            s.ScheduleID,
            s.ElderID,
            s.ScheduleName,
            CONVERT(VARCHAR(8), s.LocalTime, 108) AS LocalTime,
            u.Timezone
        FROM CheckInSchedules s
        INNER JOIN Users u ON u.UserID = s.ElderID
        WHERE s.IsActive = 1
          AND u.IsActive = 1
        ORDER BY s.ElderID, s.ScheduleName
    """)

    rows = db.execute(q).mappings().all()

    return [
        ScheduleRow(
            schedule_id=row["ScheduleID"],
            elder_id=row["ElderID"],
            schedule_name=row["ScheduleName"],
            local_time=row["LocalTime"],
            timezone_text=row["Timezone"],
        )
        for row in rows
    ]


def already_has_run(db: Session, schedule_id: int, planned_at: datetime) -> bool:
    q = text("""
        SELECT TOP 1 1
        FROM CheckInRuns
        WHERE ScheduleID = :schedule_id
          AND PlannedAt = :planned_at
    """)
    row = db.execute(q, {
        "schedule_id": schedule_id,
        "planned_at": planned_at
    }).fetchone()

    return row is not None


def create_checkin_run(db: Session, schedule_id: int, elder_id: int, planned_at: datetime) -> int:
    q = text("""
        INSERT INTO CheckInRuns (
            ScheduleID,
            ElderID,
            PlannedAt,
            Status
        )
        OUTPUT INSERTED.RunID
        VALUES (
            :schedule_id,
            :elder_id,
            :planned_at,
            'Triggered'
        )
    """)

    run_id = db.execute(q, {
        "schedule_id": schedule_id,
        "elder_id": elder_id,
        "planned_at": planned_at
    }).scalar_one()

    db.commit()
    return int(run_id)


def update_run_status(db: Session, run_id: int, status: str, note: str | None = None):
    q = text("""
        UPDATE CheckInRuns
        SET Status = :status,
            Notes = :note
        WHERE RunID = :run_id
    """)
    db.execute(q, {
        "run_id": run_id,
        "status": status,
        "note": note[:500] if note else None
    })
    db.commit()


def call_ai_checkin_start(run_id: int, elder_id: int, schedule_name: str) -> dict:
    response = requests.post(
        f"{settings.AI_BACKEND_URL}/ai/checkin/start",
        json={
            "run_id": run_id,
            "elder_id": elder_id,
            "schedule_name": schedule_name
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def run_checkin_scheduler(db: Session) -> list[dict]:
    triggered = []
    schedules = get_active_schedules(db)

    for s in schedules:
        offset_minutes = parse_offset_minutes(s.timezone_text)
        elder_local_now = local_now_for_offset(offset_minutes)

        current_hhmm = elder_local_now.strftime("%H:%M")
        target_hhmm = s.local_time[:5]   # HH:MM

        if current_hhmm != target_hhmm:
            continue

        planned_local = elder_local_now.replace(second=0, microsecond=0)
        planned_at_utc = build_planned_at_utc(planned_local, offset_minutes)

        if already_has_run(db, s.schedule_id, planned_at_utc):
            continue

        run_id = create_checkin_run(
            db=db,
            schedule_id=s.schedule_id,
            elder_id=s.elder_id,
            planned_at=planned_at_utc
        )

        try:
            ai_resp = call_ai_checkin_start(
                run_id=run_id,
                elder_id=s.elder_id,
                schedule_name=s.schedule_name
            )

            update_run_status(
                db=db,
                run_id=run_id,
                status="WaitingUser",
                note=f"AI started. ThreadID={ai_resp.get('thread_id')}"
            )

            triggered.append({
                "run_id": run_id,
                "elder_id": s.elder_id,
                "schedule_name": s.schedule_name,
                "thread_id": ai_resp.get("thread_id"),
                "message": ai_resp.get("message")
            })

        except Exception as e:
            update_run_status(
                db=db,
                run_id=run_id,
                status="Failed",
                note=f"AI backend start failed: {str(e)}"
            )

    return triggered