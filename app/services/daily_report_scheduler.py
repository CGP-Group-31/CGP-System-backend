from datetime import timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.ai_report_client import trigger_daily_report_generation
from app.utils.timezone_utils import utc_now, parse_offset_minutes


def get_active_elders_for_reports(db: Session):
    q = text("""
        SELECT UserID, Timezone
        FROM Users
        WHERE RoleID = 5
        AND IsActive = 1 AND Timezone IS NOT NULL AND LTRIM(RTRIM(Timezone)) <> ''
    """)
    return db.execute(q).mappings().all()


def report_exists_for_day(db: Session, elder_id: int, report_date: str) -> bool:
    q = text("""
        SELECT TOP 1 1
        FROM CareReports
        WHERE ElderID = :elder_id
          AND ReportType = 'daily'
          AND PeriodStart = :report_date
          AND PeriodEnd = :report_date
    """)
    row = db.execute(q, {
        "elder_id": elder_id,
        "report_date": report_date
    }).fetchone()
    return row is not None


async def run_due_daily_reports(db: Session):
    now_utc = utc_now()
    elders = get_active_elders_for_reports(db)

    for elder in elders:
        elder_id = int(elder["UserID"])
        tz_text = elder["Timezone"]

        try:
            offset_minutes = parse_offset_minutes(tz_text)
            local_now = now_utc + timedelta(minutes=offset_minutes)


            if not (local_now.hour == 0 and local_now.minute == 30):
                continue

            report_date = (local_now.date() - timedelta(days=1)).isoformat()

            if report_exists_for_day(db, elder_id, report_date):
                continue
        
            await trigger_daily_report_generation(
                elder_id=elder_id,
                report_date=report_date
            )
           

        except Exception as e:
            print(f"[daily-report] skipped elder={elder_id}, tz={tz_text!r}, error={e}")