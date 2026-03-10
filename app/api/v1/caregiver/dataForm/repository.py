from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, time, timedelta, timezone
from math import ceil
import re

_TZ_OFFSET_RE = re.compile(r"([+-])\s*(\d{2}):(\d{2})")


def cal_week_num(phone_date):
    return ceil(phone_date.day / 7)


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
        raise ValueError(f"User {user_id} not found")

    return parse_db_timezone(row["Timezone"])


def validate_submission_window(db: Session, caregiver_id: int):
    
    tz = get_user_timezone(db, caregiver_id)
    now_local = datetime.now(tz)
    current_time = now_local.time()

    start_time = time(15, 0, 0)  # 3:00 PM

    if current_time < start_time:
        raise ValueError(
            f"Inputs are allowed only from 3:00 PM to 12:00 midnight in caregiver's timezone. "
            f"Current local time: {now_local.strftime('%Y-%m-%d %H:%M:%S %z')}"
        )


def validate_user_exist(db: Session, elder_id: int, caregiver_id: int):
    query = text("""
        SELECT UserID
        FROM Users
        WHERE UserID IN (:elder_id, :caregiver_id)
    """)

    rows = db.execute(
        query,
        {"elder_id": elder_id, "caregiver_id": caregiver_id}
    ).mappings().all()

    found = {row["UserID"] for row in rows}

    if elder_id not in found:
        raise ValueError("Invalid elder_id")

    if caregiver_id not in found:
        raise ValueError("Invalid caregiver_id")


def insert_additional_elder_info(db: Session, data):
    validate_user_exist(db, data.elder_id, data.caregiver_id)
    validate_submission_window(db, data.caregiver_id)

    week_no = cal_week_num(data.phone_date)

    query = text("""
        INSERT INTO ElderAdditionalInfo (
            ElderID,
            CaregiverID,
            CognitiveBehaviorNotes,
            Preferences,
            SocialEmotionalBehaviorNotes,
            HealthGoals,
            SpecialNotesObservations,
            InfoDate,
            WeekNumber,
            RecordedAt
        )
        OUTPUT
            INSERTED.AdditionalInfoID,
            INSERTED.ElderID,
            INSERTED.CaregiverID,
            INSERTED.CognitiveBehaviorNotes,
            INSERTED.Preferences,
            INSERTED.SocialEmotionalBehaviorNotes,
            INSERTED.HealthGoals,
            INSERTED.SpecialNotesObservations,
            INSERTED.InfoDate,
            INSERTED.WeekNumber,
            INSERTED.RecordedAt
        VALUES (
            :elder_id,
            :caregiver_id,
            :cognitive_behavior_notes,
            :preferences,
            :social_emotional_behavior_notes,
            :health_goals,
            :special_notes_observations,
            :phone_date,
            :week_number,
            GETDATE()
        )
    """)

    try:
        row = db.execute(
            query,
            {
                "elder_id": data.elder_id,
                "caregiver_id": data.caregiver_id,
                "cognitive_behavior_notes": data.cognitive_behavior_notes,
                "preferences": data.preferences,
                "social_emotional_behavior_notes": data.social_emotional_behavior_notes,
                "health_goals": data.health_goals,
                "special_notes_observations": data.special_notes_observations,
                "phone_date": data.phone_date,
                "week_number": week_no,
            }
        ).mappings().first()

        if not row:
            raise RuntimeError("Insert failed")

        return dict(row)

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError("DB error while inserting additional elder information") from e


def get_last_2_info(db: Session, elder_id: int):
    query = text("""
        SELECT TOP 2
            AdditionalInfoID,
            ElderID,
            CaregiverID,
            CognitiveBehaviorNotes,
            Preferences,
            SocialEmotionalBehaviorNotes,
            HealthGoals,
            SpecialNotesObservations,
            InfoDate,
            WeekNumber,
            RecordedAt
        FROM ElderAdditionalInfo
        WHERE ElderID = :elder_id
        ORDER BY RecordedAt DESC
    """)

    try:
        rows = db.execute(query, {"elder_id": elder_id}).mappings().all()
        return [dict(row) for row in rows]
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching additional info") from e

