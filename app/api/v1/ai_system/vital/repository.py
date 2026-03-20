from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta,date
from typing import List, Dict
import pytz
def get_vitals_for_elder_in_range(db: Session, elder_id: int, start_dt, end_dt):
    q = text("""SELECT vr.RecordID, vr.ElderID, vt.VitalName, vt.Unit,
                vr.Value, vr.Notes, vr.RecordedAt
            FROM VitalRecords vr
            JOIN VitalTypes vt ON vt.VitalTypeID = vr.VitalTypeID
            WHERE vr.ElderID = :elder_id
              AND vr.RecordedAt >= :start_dt
              AND vr.RecordedAt < :end_dt
            ORDER BY vr.RecordedAt DESC""")
    rows = db.execute(q, {
        "elder_id": elder_id,
        "start_dt": start_dt,
        "end_dt": end_dt,
    }).mappings().all()
    return rows

def get_last_week_range():
    tz = pytz.timezone("Asia/Colombo")
    today = datetime.now(tz).date()
    # Monday of current week
    current_monday = today - timedelta(days=today.weekday())

    # Previous week
    last_monday = current_monday - timedelta(days=7)
    last_sunday = current_monday - timedelta(days=1)

    return last_monday, last_sunday

def generate_week_dates(start: date) -> List[date]:
    return [start + timedelta(days=i) for i in range(7)]

def get_last_week_daily_reports(db: Session, elder_id: int):
    try:
        # Check elder exists
        elder_exists = db.execute(
            text("SELECT 1 FROM Users WHERE UserID = :elder_id"),
            {"elder_id": elder_id}).scalar_one_or_none()

        if elder_exists is None:
            return None, None, None, "Elder not found."

        week_start, week_end = get_last_week_range()

        rows = db.execute(
            text("""SELECT ReportID, PeriodStart, ReportText, ReportJson,
                    GeneratedAt FROM CareReports
                WHERE ElderID = :elder_id
                  AND ReportType = 'daily'
                  AND PeriodStart BETWEEN :week_start AND :week_end
                ORDER BY PeriodStart ASC"""),
            {
                "elder_id": elder_id,
                "week_start": week_start,
                "week_end": week_end
            }
        ).mappings().all()

        # Convert DB rows to dictionary keyed by date
        db_reports: Dict[date, dict] = {}
        for row in rows:
            db_reports[row["PeriodStart"]] = {
                "report_id": row["ReportID"],
                "report_date": row["PeriodStart"],
                # "report_text": row["ReportText"],
                "report_json": row["ReportJson"],
                "generated_at": row["GeneratedAt"],
            }

        # Ensure full Mon–Sun week even if some days missing
        full_week = generate_week_dates(week_start)

        reports = []
        for day in full_week:
            if day in db_reports:
                reports.append(db_reports[day])
            else:
                reports.append({
                    "report_id": None,
                    "report_date": day,
                    # "report_text": None,
                    "report_json": None,
                    "generated_at": None,
                })

        return reports, week_start, week_end, None

    except SQLAlchemyError:
        return None, None, None, "Database error occurred."
    
    
def get_last_week_sos_logs(db: Session, elder_id: int):
    try:
        # Check elder exists
        elder_exists = db.execute(
            text("SELECT 1 FROM Users WHERE UserID = :elder_id"),
            {"elder_id": elder_id}
        ).scalar_one_or_none()

        if elder_exists is None:
            return None, None, None, "Elder not found."

        week_start, week_end = get_last_week_range()

        rows = db.execute(
            text("""SELECT s.SOSID, t.TriggerTypeName,s.TriggeredAt FROM SOSLogs s
                JOIN TriggerType t ON s.TriggerTypeID = t.TriggerTypeID
                WHERE s.ElderID = :elder_id
                  AND CAST(s.TriggeredAt AS DATE) BETWEEN :week_start AND :week_end
                ORDER BY s.TriggeredAt ASC
            """),
            {
                "elder_id": elder_id,
                "week_start": week_start,
                "week_end": week_end
            }
        ).mappings().all()

        sos_logs = []
        for row in rows:
            sos_logs.append({
                "sos_id": row["SOSID"],
                "trigger_type": row["TriggerTypeName"],
                "triggered_at": row["TriggeredAt"].strftime("%a, %d %b %H:%M"),
            })

        return sos_logs, week_start, week_end, None

    except SQLAlchemyError:
        return None, None, None, "Database error occurred while fetching SOS logs."