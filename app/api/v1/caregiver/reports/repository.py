from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def get_last_10_care_reports(db: Session, elder_id: int):
    try:
        # optional elder existence check
        elder_exists = db.execute(
            text("SELECT 1 FROM Users WHERE UserID = :elder_id"),
            {"elder_id": elder_id}
        ).scalar_one_or_none()

        if elder_exists is None:
            return None, "Elder not found."

        rows = db.execute(
            text("""
                SELECT TOP 10
                    ReportID,
                    ElderID,
                    ReportType,
                    PeriodStart,
                    PeriodEnd,
                    ReportText,
                    GeneratedAt
                FROM CareReports
                WHERE ElderID = :elder_id
                  AND ReportType IN ('daily', 'weekly')
                ORDER BY GeneratedAt DESC, ReportID DESC
            """),
            {"elder_id": elder_id}
        ).mappings().all()

        reports = []
        for row in rows:
            reports.append({
                "report_id": row["ReportID"],
                "elder_id": row["ElderID"],
                "report_type": row["ReportType"],
                "period_start": row["PeriodStart"],
                "period_end": row["PeriodEnd"],
                "report_text": row["ReportText"],
                "generated_at": row["GeneratedAt"],
            })

        return reports, None

    except SQLAlchemyError:
        return None, "Database error occurred while fetching care reports."