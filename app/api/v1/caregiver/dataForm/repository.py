from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, time, timedelta, timezone
from math import ceil


def cal_week_num(phone_date):
    return ceil(phone_date.day / 7)


def validate_submission_window():
    
    now_server = datetime.now()
    current_time = now_server.time()

    start_time = time(15, 0, 0)  # 3:00 PM
    end_time = time(23, 59, 59)

    if not (start_time <= current_time <= end_time):
        raise ValueError(
            f"Inputs are allowed only from 3:00 PM to 12:00 midnight in caregiver's timezone. "
            f"Current local time: {now_server.strftime('%Y-%m-%d %H:%M:%S %z')}"
        )
    return now_server


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
    

def validate_weekly_submission(db: Session, elder_id: int, caregiver_id: int, current_date):
    week_no = cal_week_num(current_date)
    month_no = current_date.month
    year_no = current_date.year

    query = text("""
        SELECT TOP 1 AdditionalInfoID
        FROM ElderAdditionalInfo
        WHERE ElderID = :elder_id
          AND CaregiverID = :caregiver_id
          AND WeekNumber = :week_number
          AND MONTH(InfoDate) = :month_no
          AND YEAR(InfoDate) = :year_no
    """)

    row = db.execute(
        query,
        {
            "elder_id": elder_id,
            "caregiver_id": caregiver_id,
            "week_number": week_no,
            "month_no": month_no,
            "year_no": year_no
        }
    ).mappings().first()

    if row:
        raise ValueError("Weekly observation already submitted for this elder in the current week.")


def insert_additional_elder_info(db: Session, data):
    validate_user_exist(db, data.elder_id, data.caregiver_id)

    now_sever = validate_submission_window()
    current_date = now_sever.date()
    week_no = cal_week_num(current_date)

    validate_weekly_submission(db, data.elder_id, data.caregiver_id, current_date)

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

