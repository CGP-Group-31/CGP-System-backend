from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import re


def _make_title(report_type: str) -> str:
    return (
        "Daily Caregiver Report"
        if report_type == "daily"
        else "Weekly Caregiver Report"
    )


def get_last_10_care_reports(db: Session, elder_id: int):
    try:
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
                "title": _make_title(row["ReportType"]),
                "period_start": row["PeriodStart"],
                "period_end": row["PeriodEnd"],
                "generated_at": row["GeneratedAt"],
            })

        return {"reports": reports, "total": len(reports)}, None

    except SQLAlchemyError as e:
        print("DB ERROR in get_last_10_care_reports:", e)
        return None, "Database error occurred while fetching care reports."


def list_care_reports(
    db: Session,
    elder_id: int,
    report_type: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
    try:
        elder_exists = db.execute(
            text("SELECT 1 FROM Users WHERE UserID = :elder_id"),
            {"elder_id": elder_id}
        ).scalar_one_or_none()

        if elder_exists is None:
            return None, "Elder not found."

        where_parts = [
            "ElderID = :elder_id",
            "ReportType IN ('daily', 'weekly')",
        ]
        params = {
            "elder_id": elder_id,
            "limit": limit,
            "offset": offset,
        }

        if report_type in ("daily", "weekly"):
            where_parts.append("ReportType = :report_type")
            params["report_type"] = report_type

        if search and search.strip():
            where_parts.append("""
                (
                    ReportText LIKE :search
                    OR ReportType LIKE :search
                    OR CONVERT(VARCHAR(10), PeriodStart, 120) LIKE :search
                    OR CONVERT(VARCHAR(10), PeriodEnd, 120) LIKE :search
                )
            """)
            params["search"] = f"%{search.strip()}%"

        where_sql = " AND ".join(where_parts)

        rows = db.execute(
            text(f"""
                SELECT
                    ReportID,
                    ElderID,
                    ReportType,
                    PeriodStart,
                    PeriodEnd,
                    GeneratedAt
                FROM CareReports
                WHERE {where_sql}
                ORDER BY GeneratedAt DESC, ReportID DESC
                OFFSET :offset ROWS
                FETCH NEXT :limit ROWS ONLY
            """),
            params
        ).mappings().all()

        total = db.execute(
            text(f"""
                SELECT COUNT(*)
                FROM CareReports
                WHERE {where_sql}
            """),
            params
        ).scalar_one()

        reports = []
        for row in rows:
            reports.append({
                "report_id": row["ReportID"],
                "elder_id": row["ElderID"],
                "report_type": row["ReportType"],
                "title": _make_title(row["ReportType"]),
                "period_start": row["PeriodStart"],
                "period_end": row["PeriodEnd"],
                "generated_at": row["GeneratedAt"],
            })

        return {"reports": reports, "total": total}, None

    except SQLAlchemyError as e:
        print("DB ERROR in list_care_reports:", e)
        return None, "Database error occurred while fetching care reports."


def _get_elder_form_for_date(db: Session, elder_id: int, report_date):
    form = db.execute(
        text("""
            SELECT TOP 1
                CheckInID,
                Mood,
                SleepQuantity,
                WaterIntake,
                AppetiteLevel,
                EnergyLevel,
                OverallDay,
                MovementToday,
                LonelinessLevel,
                TalkInteraction,
                StressLevel,
                InfoDate
            FROM ElderForm
            WHERE ElderID = :elder_id
              AND InfoDate = :report_date
            ORDER BY RecordedAt DESC
        """),
        {"elder_id": elder_id, "report_date": report_date}
    ).mappings().first()

    if not form:
        form = db.execute(
            text("""
                SELECT TOP 1
                    CheckInID,
                    Mood,
                    SleepQuantity,
                    WaterIntake,
                    AppetiteLevel,
                    EnergyLevel,
                    OverallDay,
                    MovementToday,
                    LonelinessLevel,
                    TalkInteraction,
                    StressLevel,
                    InfoDate
                FROM ElderForm
                WHERE ElderID = :elder_id
                  AND InfoDate <= :report_date
                ORDER BY InfoDate DESC, RecordedAt DESC
            """),
            {"elder_id": elder_id, "report_date": report_date}
        ).mappings().first()

    if not form:
        return None, [], []

    check_in_id = form["CheckInID"]

    pain_rows = db.execute(
        text("""
            SELECT PainArea
            FROM ElderFormInPain
            WHERE CheckInID = :check_in_id
            ORDER BY CheckInPainID
        """),
        {"check_in_id": check_in_id}
    ).mappings().all()

    activity_rows = db.execute(
        text("""
            SELECT ActivityName
            FROM ElderFormActivity
            WHERE CheckInID = :check_in_id
            ORDER BY CheckInActivityID
        """),
        {"check_in_id": check_in_id}
    ).mappings().all()

    overview = {
        "mood": form["Mood"],
        "sleep_quantity": form["SleepQuantity"],
        "water_intake": form["WaterIntake"],
        "appetite_level": form["AppetiteLevel"],
        "energy_level": form["EnergyLevel"],
        "overall_day": form["OverallDay"],
        "movement_today": form["MovementToday"],
        "loneliness_level": form["LonelinessLevel"],
        "talk_interaction": form["TalkInteraction"],
        "stress_level": form["StressLevel"],
    }

    pain_areas = [r["PainArea"] for r in pain_rows]
    activities = [r["ActivityName"] for r in activity_rows]

    return overview, pain_areas, activities


def _get_medication_adherence_for_date(db: Session, elder_id: int, report_date):
    rows = db.execute(
        text("""
            SELECT
                ma.StatusID,
                m.MedicationName
            FROM MedicationAdherence ma
            INNER JOIN MedicationSchedules ms
                ON ma.ScheduleID = ms.ScheduleID
            INNER JOIN Medications m
                ON ms.MedicationID = m.MedicationID
            WHERE ma.ElderID = :elder_id
              AND CAST(ma.ScheduledFor AS DATE) = :report_date
        """),
        {"elder_id": elder_id, "report_date": report_date}
    ).mappings().all()

    taken_count = 0
    missed_count = 0
    missed_items = []

    for row in rows:
        status_id = row["StatusID"]
        med_name = row["MedicationName"]

        if status_id == 2:  # Taken
            taken_count += 1
        elif status_id == 3:  # Missed
            missed_count += 1
            missed_items.append(f"{med_name} missed")

    return {
        "taken_count": taken_count,
        "missed_count": missed_count,
        "missed_items": missed_items,
    }


def _get_meal_adherence_for_date(db: Session, elder_id: int, report_date):
    rows = db.execute(
        text("""
            SELECT
                MealTime,
                StatusID
            FROM MealAdherence
            WHERE ElderID = :elder_id
              AND CAST(ScheduledFor AS DATE) = :report_date
        """),
        {"elder_id": elder_id, "report_date": report_date}
    ).mappings().all()

    meal_map = {
        "BREAKFAST": None,
        "LUNCH": None,
        "DINNER": None,
    }

    status_map = {
        1: "Pending",
        2: "Eaten",
        3: "Missed",
        4: "Skipped",
    }

    for row in rows:
        meal_time = str(row["MealTime"]).upper()
        status_name = status_map.get(row["StatusID"], "Unknown")
        if meal_time in meal_map:
            meal_map[meal_time] = status_name

    return {
        "breakfast": meal_map["BREAKFAST"],
        "lunch": meal_map["LUNCH"],
        "dinner": meal_map["DINNER"],
    }


def _get_ai_checkin_insights(db: Session, elder_id: int):
    row = db.execute(
        text("""
            SELECT TOP 1
                CognitiveBehaviorNotes,
                SocialEmotionalBehaviorNotes,
                SpecialNotesObservations
            FROM ElderAdditionalInfo
            WHERE ElderID = :elder_id
            ORDER BY RecordedAt DESC
        """),
        {"elder_id": elder_id}
    ).mappings().first()

    if not row:
        return None

    parts = []
    if row["CognitiveBehaviorNotes"]:
        parts.append(str(row["CognitiveBehaviorNotes"]).strip())
    if row["SocialEmotionalBehaviorNotes"]:
        parts.append(str(row["SocialEmotionalBehaviorNotes"]).strip())
    if row["SpecialNotesObservations"]:
        parts.append(str(row["SpecialNotesObservations"]).strip())

    if not parts:
        return None

    return " ".join(parts)


def _build_concerns(overview, medication_adherence, meal_adherence, pain_areas):
    concerns = []

    if medication_adherence["missed_count"] > 0:
        concerns.append("Missed medication detected")

    if meal_adherence.get("dinner") == "Skipped":
        concerns.append("Skipped dinner")

    if overview:
        if overview.get("stress_level") == "Yes":
            concerns.append("High stress level reported")
        if overview.get("loneliness_level") == "Always":
            concerns.append("High loneliness reported")
        if overview.get("overall_day") == "Not Good":
            concerns.append("Overall day reported as not good")

    if pain_areas and "None" not in pain_areas:
        concerns.append(f"Pain reported: {', '.join(pain_areas)}")

    return concerns


def _build_caregiver_recommendation(concerns):
    if not concerns:
        return "No major issues detected today. Continue normal monitoring and support."

    if "Missed medication detected" in concerns and "Skipped dinner" in concerns:
        return "Please follow up on missed medication and encourage a proper evening meal."

    if "High stress level reported" in concerns:
        return "Provide reassurance and check for emotional or environmental stress triggers."

    if "High loneliness reported" in concerns:
        return "Try to increase social engagement and check in more frequently today."

    return "Review the concerns noted in this report and follow up with the elder if needed."


def get_care_report_detail(db: Session, elder_id: int, report_id: int):
    try:
        elder_exists = db.execute(
            text("SELECT 1 FROM Users WHERE UserID = :elder_id"),
            {"elder_id": elder_id}
        ).scalar_one_or_none()

        if elder_exists is None:
            return None, "Elder not found."

        row = db.execute(
            text("""
                SELECT
                    ReportID,
                    ElderID,
                    ReportType,
                    PeriodStart,
                    PeriodEnd,
                    ReportText,
                    GeneratedAt
                FROM CareReports
                WHERE ElderID = :elder_id
                  AND ReportID = :report_id
                  AND ReportType IN ('daily', 'weekly')
            """),
            {"elder_id": elder_id, "report_id": report_id}
        ).mappings().first()

        if not row:
            return None, "Report not found."

        report_type = row["ReportType"]
        report_date = row["PeriodStart"]
        parsed_text = _parse_report_text(row["ReportText"])

        overview, pain_areas, activities = _get_elder_form_for_date(
            db, elder_id, report_date
        )
        medication_adherence = _get_medication_adherence_for_date(
            db, elder_id, report_date
        )
        meal_adherence = _get_meal_adherence_for_date(
            db, elder_id, report_date
        )
        ai_checkin_insights = _get_ai_checkin_insights(db, elder_id)

        # fallback to parsed report text if DB values are missing
        if not overview:
            overview = parsed_text["elder_day_overview"]

        if not pain_areas:
            pain_areas = parsed_text["pain_areas"]

        if not activities:
            activities = parsed_text["activities"]

        if not ai_checkin_insights:
            ai_checkin_insights = parsed_text["ai_checkin_insights"]

        if not meal_adherence.get("breakfast"):
            meal_adherence["breakfast"] = parsed_text["meal_adherence"]["breakfast"]

        if not meal_adherence.get("lunch"):
            meal_adherence["lunch"] = parsed_text["meal_adherence"]["lunch"]

        if not meal_adherence.get("dinner"):
            meal_adherence["dinner"] = parsed_text["meal_adherence"]["dinner"]

        concerns = _build_concerns(
            overview,
            medication_adherence,
            meal_adherence,
            pain_areas,
        )

        if not concerns:
            concerns = parsed_text["concerns"]

        caregiver_recommendation = _build_caregiver_recommendation(concerns)

        if parsed_text["caregiver_recommendation"]:
            caregiver_recommendation = parsed_text["caregiver_recommendation"]

        return {
            "report_id": row["ReportID"],
            "elder_id": row["ElderID"],
            "report_type": report_type,
            "title": _make_title(report_type),
            "period_start": row["PeriodStart"],
            "period_end": row["PeriodEnd"],
            "generated_at": row["GeneratedAt"],
            "report_text": row["ReportText"],
            "elder_day_overview": overview,
            "pain_report": {"pain_areas": pain_areas},
            "activities": activities,
            "ai_checkin_insights": ai_checkin_insights,
            "medication_adherence": medication_adherence,
            "meal_adherence": meal_adherence,
            "concerns": concerns,
            "caregiver_recommendation": caregiver_recommendation,
        }, None

    except SQLAlchemyError as e:
        print("DB ERROR in get_care_report_detail:", e)
        return None, "Database error occurred while fetching report detail."


def _parse_report_text(report_text: str):
    parsed = {
        "elder_day_overview": None,
        "pain_areas": [],
        "activities": [],
        "ai_checkin_insights": None,
        "medication_adherence_text": None,
        "meal_adherence": {
            "breakfast": None,
            "lunch": None,
            "dinner": None,
        },
        "concerns": [],
        "caregiver_recommendation": None,
    }

    if not report_text or not report_text.strip():
        return parsed

    lines = [line.strip() for line in report_text.splitlines() if line.strip()]

    overview = {}

    for line in lines:
        if line.startswith("- Mood:"):
            overview["mood"] = line.replace("- Mood:", "").strip()

        elif line.startswith("- Sleep:"):
            overview["sleep_quantity"] = line.replace("- Sleep:", "").strip()

        elif line.startswith("- Water Intake:"):
            overview["water_intake"] = line.replace("- Water Intake:", "").strip()

        elif line.startswith("- Appetite:"):
            overview["appetite_level"] = line.replace("- Appetite:", "").strip()

        elif line.startswith("- Energy:"):
            overview["energy_level"] = line.replace("- Energy:", "").strip()

        elif line.startswith("- Overall Day:"):
            overview["overall_day"] = line.replace("- Overall Day:", "").strip()

        elif line.startswith("- Movement:"):
            overview["movement_today"] = line.replace("- Movement:", "").strip()

        elif line.startswith("- Loneliness:"):
            overview["loneliness_level"] = line.replace("- Loneliness:", "").strip()

        elif line.startswith("- Social Interaction:"):
            overview["talk_interaction"] = line.replace("- Social Interaction:", "").strip()

        elif line.startswith("- Stress:"):
            overview["stress_level"] = line.replace("- Stress:", "").strip()

        elif line.startswith("- Pain Report:"):
            pain_text = line.replace("- Pain Report:", "").strip()
            if pain_text and pain_text.lower() != "none":
                parsed["pain_areas"] = [p.strip() for p in pain_text.split(",") if p.strip()]

        elif line.startswith("Activities:"):
            activity_text = line.replace("Activities:", "").strip()
            if activity_text and activity_text.lower() != "none":
                parsed["activities"] = [a.strip() for a in activity_text.split(",") if a.strip()]

        elif line.startswith("- AI Check-In Insights:"):
            parsed["ai_checkin_insights"] = line.replace("- AI Check-In Insights:", "").strip()

        elif line.startswith("- Medication Adherence:"):
            parsed["medication_adherence_text"] = line.replace("- Medication Adherence:", "").strip()

        elif line.startswith("Meal Adherence:"):
            meal_text = line.replace("Meal Adherence:", "").strip()

            breakfast_match = re.search(r"Breakfast=([^,]+)", meal_text)
            lunch_match = re.search(r"Lunch=([^,]+)", meal_text)
            dinner_match = re.search(r"Dinner=([^,]+)", meal_text)

            if breakfast_match:
                parsed["meal_adherence"]["breakfast"] = breakfast_match.group(1).strip()
            if lunch_match:
                parsed["meal_adherence"]["lunch"] = lunch_match.group(1).strip()
            if dinner_match:
                parsed["meal_adherence"]["dinner"] = dinner_match.group(1).strip()

        elif line.startswith("Concerns:"):
            concerns_text = line.replace("Concerns:", "").strip()
            if concerns_text.lower() != "none significant noted." and concerns_text.lower() != "none":
                parsed["concerns"] = [c.strip() for c in concerns_text.split(",") if c.strip()]

        elif line.startswith("Caregiver Recommendations:"):
            parsed["caregiver_recommendation"] = line.replace(
                "Caregiver Recommendations:", ""
            ).strip()

    if overview:
        parsed["elder_day_overview"] = overview

    return parsed