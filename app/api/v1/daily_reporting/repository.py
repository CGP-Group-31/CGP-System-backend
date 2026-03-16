from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import date

def get_daily_medication_summary(db: Session, elder_id: int, report_date: date):

    items_query = text("""
        SELECT
            m.MedicationName AS medication_name,
            m.Dosage AS dosage,
            ma.ScheduledFor AS scheduled_for,
            s.StatusName AS status
        FROM MedicationAdherence ma
        JOIN MedicationSchedules ms ON ms.ScheduleID = ma.ScheduleID
        JOIN Medications m ON m.MedicationID = ms.MedicationID
        JOIN Status s ON s.StatusID = ma.StatusID
        WHERE ma.ElderID = :eid
        AND CAST(ma.ScheduledFor AS date) = :report_date
        ORDER BY ma.ScheduledFor ASC
    """)

    try:
        items = db.execute(items_query, {"eid": elder_id, "report_date": report_date}).mappings().all()

        return {
            "elder_id": elder_id,
            "date": str(report_date),
            "items": items
        }

    except SQLAlchemyError as e:
        raise RuntimeError("DB error while building medication report") from e



def get_daily_meal_summary(db: Session, elder_id: int, report_date: date):

    query = text("""
        SELECT
            m.MealTime AS meal_time,
            s.StatusName AS status
        FROM MealAdherence m
        JOIN Status s ON s.StatusID = m.StatusID
        WHERE m.ElderID = :eid
        AND CAST(m.ScheduledFor AS date) =:report_date
        ORDER BY m.ScheduledFor ASC
    """)

    try:
        rows = db.execute(query, {"eid": elder_id, "report_date":report_date}).mappings().all()

        breakfast = "No data"
        lunch = "No data"
        dinner = "No data"

        items = []

        for r in rows:
            meal = r["meal_time"].upper()
            status = r["status"]

            items.append({
                "meal_time": meal,
                "status": status
            })

            if meal == "BREAKFAST":
                breakfast = status
            elif meal == "LUNCH":
                lunch = status
            elif meal == "DINNER":
                dinner = status

        return {
            "elder_id": elder_id,
            "date": report_date,
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
            "items": items
        }

    except SQLAlchemyError as e:
        raise RuntimeError(f"DB error while building meal report: {str(e)}") from e