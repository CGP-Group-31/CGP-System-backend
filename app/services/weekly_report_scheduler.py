from datetime import timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services.ai_report_client import trigger_weekly_report_generation
from app.utils.timezone_utils import utc_now, parse_offset_minutes


def get_active_elders_for_reports(db: Session):
    q = text("""
        SELECT UserID, Timezone
        FROM Users
        WHERE RoleID = 5
        AND IsActive = 1
        AND Timezone IS NOT NULL
        AND LTRIM(RTRIM(Timezone)) <> ''
    """)
    return db.execute(q).mappings().all()


def report_exists_for_week(db: Session, elder_id: int, week_start: str, week_end: str) -> bool:
    q = text("""
        SELECT TOP 1 1
        FROM CareReports
        WHERE ElderID = :elder_id
        AND ReportType = 'weekly'
        AND PeriodStart = :week_start
        AND PeriodEnd = :week_end
    """)

    row = db.execute(q, {
        "elder_id": elder_id,
        "week_start": week_start,
        "week_end": week_end
    }).fetchone()

    return row is not None


async def run_due_weekly_reports(db: Session):

    now_utc = utc_now()

    elders = get_active_elders_for_reports(db)

    for elder in elders:

        elder_id = int(elder["UserID"])
        tz_text = elder["Timezone"]

        try:

            offset_minutes = parse_offset_minutes(tz_text)
            local_now = now_utc + timedelta(minutes=offset_minutes)

            # Monday = 0
            if not (
                local_now.weekday() == 0
                and local_now.hour == 2
                
            ):
                continue

            week_end_date = local_now.date() - timedelta(days=1)
            week_start_date = week_end_date - timedelta(days=6)

            week_start = week_start_date.isoformat()
            week_end = week_end_date.isoformat()

            if report_exists_for_week(db, elder_id, week_start, week_end):
                continue

            await trigger_weekly_report_generation(
                elder_id=elder_id,
                week_start=week_start,
                week_end=week_end
            )

        except Exception as e:

            print(
                f"[weekly-report] skipped elder={elder_id}, "
                f"tz={tz_text}, error={e}"
            )