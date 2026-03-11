from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

PENDING_STATUS_ID = 1
TAKEN_STATUS_ID = 2
MISSED_STATUS_ID = 3


def get_today_scheduled_for_reminders(db: Session, elder_id: int):
    query = text("""
        SELECT
            ma.AdherenceID,
            ma.ElderID,
            ma.ScheduleID,
            ma.ScheduledFor,
            ma.TakenAt,
            ma.StatusID,
            m.MedicationID,
            m.Dosage,
            m.MedicationName
        FROM MedicationAdherence ma
        INNER JOIN MedicationSchedules ms
            ON ms.ScheduleID = ma.ScheduleID
        INNER JOIN Medications m
            ON m.MedicationID = ms.MedicationID
        WHERE ma.ElderID = :elder_id
          AND CAST(ma.ScheduledFor AS date) = CAST(GETDATE() AS date)
          AND ma.StatusID = :status_id
        ORDER BY ma.ScheduledFor ASC
    """)
    try:
        return db.execute(
            query,
            {"elder_id": elder_id, "status_id": PENDING_STATUS_ID}
        ).mappings().all()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching today's scheduled medicine") from e


def get_today_taken_for_reminders(db: Session, elder_id: int):
    query = text("""
        SELECT
            ma.AdherenceID,
            ma.ElderID,
            ma.ScheduleID,
            ma.ScheduledFor,
            ma.TakenAt,
            ma.StatusID,
            m.MedicationID,
            m.Dosage,
            m.MedicationName
        FROM MedicationAdherence ma
        INNER JOIN MedicationSchedules ms
            ON ms.ScheduleID = ma.ScheduleID
        INNER JOIN Medications m
            ON m.MedicationID = ms.MedicationID
        WHERE ma.ElderID = :elder_id
          AND CAST(ma.ScheduledFor AS date) = CAST(GETDATE() AS date)
          AND ma.StatusID = :status_id
        ORDER BY ma.TakenAt DESC
    """)
    try:
        return db.execute(
            query,
            {"elder_id": elder_id, "status_id": TAKEN_STATUS_ID}
        ).mappings().all()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching today's taken medicine") from e


def get_today_missed_for_reminders(db: Session, elder_id: int):
    query = text("""
        SELECT
            ma.AdherenceID,
            ma.ElderID,
            ma.ScheduleID,
            ma.ScheduledFor,
            ma.TakenAt,
            ma.StatusID,
            m.MedicationID,
            m.Dosage,
            m.MedicationName
        FROM MedicationAdherence ma
        INNER JOIN MedicationSchedules ms
            ON ms.ScheduleID = ma.ScheduleID
        INNER JOIN Medications m
            ON m.MedicationID = ms.MedicationID
        WHERE ma.ElderID = :elder_id
          AND CAST(ma.ScheduledFor AS date) = CAST(GETDATE() AS date)
          AND ma.StatusID = :status_id
        ORDER BY ma.ScheduledFor ASC
    """)
    try:
        return db.execute(
            query,
            {"elder_id": elder_id, "status_id": MISSED_STATUS_ID}
        ).mappings().all()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching today's missed medicine") from e