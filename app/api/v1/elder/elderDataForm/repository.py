from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, time, timezone, timedelta
import re


VALID_MOODS = {"Happy", "Sad", "Neutral"}
VALID_APPETITE = {"Good", "Normal", "Low"}
VALID_ENERGY = {"Good", "Normal", "Low"}
VALID_OVERALL_DAY = {"Good", "Okay", "Not Good"}
VALID_MOVEMENT = {
    "Moved around the house alot",
    "Moved around the house a little",
    "Went outside (more than 30 min)",
    "Went outside (less than 30 min)",
    "Mostly Resting",
}
VALID_LONELINESS = {"Not Lonely", "Sometimes", "Always"}
VALID_TALK = {
    "Yes, with several people",
    "Yes, with one person",
    "Just a quick Hello",
    "No interaction",
}
VALID_STRESS = {"No", "A little", "Yes"}

VALID_PAIN_AREAS = {"Head", "Neck", "Chest", "Legs", "Back", "Arms", "Other", "None"}
VALID_ACTIVITIES = {
    "House work",
    "Exercise",
    "Gardening",
    "Watching TV",
    "Sewing",
    "Mostly resting",
    "None",
}

_TZ_OFFSET_RE = re.compile(r"([+-])\s*(\d{2}):(\d{2})")


def parse_db_timezone(tz_value: str):

    if tz_value is None:
        raise ValueError("User timezone is missing")

    tz_str = str(tz_value).strip()
    if not tz_str:
        raise ValueError("User timezone is missing")

    match = _TZ_OFFSET_RE.search(tz_str)
    if not match:
        raise ValueError(f"Invalid timezone format in DB: {tz_str}")

    sign, hours, minutes = match.groups()
    hours = int(hours)
    minutes = int(minutes)

    offset = timedelta(hours=hours, minutes=minutes)
    if sign == "-":
        offset = -offset

    return timezone(offset, name=tz_str)


def get_user_timezone(db: Session, user_id: int):
    query = text("""
        SELECT Timezone
        FROM Users
        WHERE UserID = :user_id
    """)
    row = db.execute(query, {"user_id": user_id}).mappings().first()

    if not row:
        raise ValueError("User not found")

    return parse_db_timezone(row["Timezone"])


def validate_submission_window(db: Session, elder_id: int):

    tz = get_user_timezone(db, elder_id)
    now_local = datetime.now(tz)
    current_time = now_local.time()

    start_time = time(15, 0, 0)  
    end_time = time(23, 59, 59)

    if not (start_time <= current_time <= end_time):
        raise ValueError(
            f"Inputs are allowed only from 3:00 PM to 12:00 AM in the elder's timezone. "
            f"Current local time: {now_local.strftime('%Y-%m-%d %H:%M:%S %z')}"
        )


def _validate_choice(value: str, valid_set: set[str], field_name: str):
    if value not in valid_set:
        raise ValueError(f"Invalid {field_name}: {value}")


def _validate_multi(values: list[str], valid_set: set[str], field_name: str):
    if not values:
        raise ValueError(f"At least one {field_name} must be selected")

    for v in values:
        if v not in valid_set:
            raise ValueError(f"Invalid {field_name}: {v}")

    if "None" in values and len(values) > 1:
        raise ValueError(f"'None' cannot be combined with other {field_name}s")


def validate_elder_exists(db: Session, elder_id: int):
    query = text("""
        SELECT UserID
        FROM Users
        WHERE UserID = :elder_id
    """)
    row = db.execute(query, {"elder_id": elder_id}).mappings().first()

    if not row:
        raise ValueError("Invalid elder_id")


def validate_not_already_submitted(db: Session, elder_id: int, info_date):
    query = text("""
        SELECT TOP 1 CheckInID
        FROM ElderForm
        WHERE ElderID = :elder_id
          AND InfoDate = :info_date
    """)
    row = db.execute(
        query,
        {"elder_id": elder_id, "info_date": info_date}
    ).mappings().first()

    if row:
        raise ValueError("Form already submitted for this date")


def insert_elder_form(db: Session, data):
    validate_elder_exists(db, data.elder_id)
    validate_submission_window(db, data.elder_id)
    validate_not_already_submitted(db, data.elder_id, data.info_date)

    _validate_choice(data.mood, VALID_MOODS, "mood")
    _validate_choice(data.appetite_level, VALID_APPETITE, "appetite_level")
    _validate_choice(data.energy_level, VALID_ENERGY, "energy_level")
    _validate_choice(data.overall_day, VALID_OVERALL_DAY, "overall_day")
    _validate_choice(data.movement_today, VALID_MOVEMENT, "movement_today")
    _validate_choice(data.loneliness_level, VALID_LONELINESS, "loneliness_level")
    _validate_choice(data.talk_interaction, VALID_TALK, "talk_interaction")
    _validate_choice(data.stress_level, VALID_STRESS, "stress_level")

    _validate_multi(data.pain_areas, VALID_PAIN_AREAS, "pain area")
    _validate_multi(data.activities, VALID_ACTIVITIES, "activity")

    insert_main = text("""
        INSERT INTO ElderForm (
            ElderID,
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
        )
        OUTPUT
            INSERTED.CheckInID,
            INSERTED.ElderID,
            INSERTED.InfoDate,
            INSERTED.RecordedAt
        VALUES (
            :elder_id,
            :mood,
            :sleep_quantity,
            :water_intake,
            :appetite_level,
            :energy_level,
            :overall_day,
            :movement_today,
            :loneliness_level,
            :talk_interaction,
            :stress_level,
            :info_date
        )
    """)

    insert_pain = text("""
        INSERT INTO ElderFormInPain (
            CheckInID,
            PainArea
        )
        VALUES (
            :check_in_id,
            :pain_area
        )
    """)

    insert_activity = text("""
        INSERT INTO ElderFormActivity (
            CheckInID,
            ActivityName
        )
        VALUES (
            :check_in_id,
            :activity_name
        )
    """)

    try:
        main_row = db.execute(insert_main, {
            "elder_id": data.elder_id,
            "mood": data.mood,
            "sleep_quantity": data.sleep_quantity,
            "water_intake": data.water_intake,
            "appetite_level": data.appetite_level,
            "energy_level": data.energy_level,
            "overall_day": data.overall_day,
            "movement_today": data.movement_today,
            "loneliness_level": data.loneliness_level,
            "talk_interaction": data.talk_interaction,
            "stress_level": data.stress_level,
            "info_date": data.info_date,
        }).mappings().first()

        if not main_row:
            raise RuntimeError("Failed to insert elder form")

        check_in_id = main_row["CheckInID"]

        for pain_area in data.pain_areas:
            db.execute(insert_pain, {
                "check_in_id": check_in_id,
                "pain_area": pain_area
            })

        for activity in data.activities:
            db.execute(insert_activity, {
                "check_in_id": check_in_id,
                "activity_name": activity
            })

        return {
            "message": "Elder form submitted successfully",
            "check_in_id": main_row["CheckInID"],
            "elder_id": main_row["ElderID"],
            "info_date": main_row["InfoDate"],
            "recorded_at": main_row["RecordedAt"],
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError("DB error while inserting elder form") from e


def get_latest_elder_form(db: Session, elder_id: int):
    main_query = text("""
        SELECT TOP 1
            CheckInID,
            ElderID,
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
            InfoDate,
            RecordedAt
        FROM ElderForm
        WHERE ElderID = :elder_id
        ORDER BY RecordedAt DESC
    """)

    try:
        main_row = db.execute(main_query, {"elder_id": elder_id}).mappings().first()

        if not main_row:
            return None

        check_in_id = main_row["CheckInID"]

        pain_query = text("""
            SELECT PainArea
            FROM ElderFormInPain
            WHERE CheckInID = :check_in_id
            ORDER BY CheckInPainID
        """)
        pain_rows = db.execute(
            pain_query,
            {"check_in_id": check_in_id}
        ).mappings().all()

        activity_query = text("""
            SELECT ActivityName
            FROM ElderFormActivity
            WHERE CheckInID = :check_in_id
            ORDER BY CheckInActivityID
        """)
        activity_rows = db.execute(
            activity_query,
            {"check_in_id": check_in_id}
        ).mappings().all()

        return {
            "check_in_id": main_row["CheckInID"],
            "elder_id": main_row["ElderID"],
            "mood": main_row["Mood"],
            "sleep_quantity": main_row["SleepQuantity"],
            "water_intake": main_row["WaterIntake"],
            "appetite_level": main_row["AppetiteLevel"],
            "energy_level": main_row["EnergyLevel"],
            "overall_day": main_row["OverallDay"],
            "movement_today": main_row["MovementToday"],
            "loneliness_level": main_row["LonelinessLevel"],
            "talk_interaction": main_row["TalkInteraction"],
            "stress_level": main_row["StressLevel"],
            "pain_areas": [r["PainArea"] for r in pain_rows],
            "activities": [r["ActivityName"] for r in activity_rows],
            "info_date": main_row["InfoDate"],
            "recorded_at": main_row["RecordedAt"],
        }

    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching latest elder form") from e