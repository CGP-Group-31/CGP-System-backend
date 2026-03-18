from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


def get_additional_info_by_elder(db: Session, elder_id: int):
    query = text("""
        SELECT
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


def get_additional_info_by_elder_in_range(db: Session, elder_id: int, start_date, end_date):
    query = text("""
        SELECT
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
          AND InfoDate >= :start_date
          AND InfoDate < :end_date
        ORDER BY RecordedAt DESC
    """)

    try:
        rows = db.execute(query, {
            "elder_id": elder_id,
            "start_date": start_date,
            "end_date": end_date,
        }).mappings().all()
        return [dict(row) for row in rows]
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching additional info") from e


def get_additional_info_by_elder_month_week(db: Session, elder_id: int, year: int, month: int, week_number: int):
    query = text("""
        SELECT
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
          AND YEAR(InfoDate) = :year
          AND MONTH(InfoDate) = :month
          AND WeekNumber = :week_number
        ORDER BY RecordedAt DESC
    """)

    try:
        rows = db.execute(query, {
            "elder_id": elder_id,
            "year": year,
            "month": month,
            "week_number": week_number,
        }).mappings().all()
        return [dict(row) for row in rows]
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching additional info") from e
