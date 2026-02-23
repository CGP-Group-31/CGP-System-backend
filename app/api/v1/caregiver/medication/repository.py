# app/modules/medication/repository.py
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


def create_medication(db: Session, data) -> int:
    query = text("""INSERT INTO Medications (ElderID, MedicationName, Dosage, Instructions, CreatedBy)
        OUTPUT INSERTED.MedicationID
        VALUES (:elder_id, :name, :dosage, :instructions, :created_by);""")

    result = db.execute(query, {
        "elder_id": data.elderId,
        "name": data.name,
        "dosage": data.dosage,
        "instructions": data.instructions,
        "created_by": data.caregiverId
    })
    return int(result.scalar())


def create_medication_schedules(
    db: Session,
    medication_id: int,
    times: list[str],
    repeat_days: str,
    start_date,
    end_date
) -> None:
    query = text("""INSERT INTO MedicationSchedules (MedicationID, TimeOfDay, RepeatDays, StartDate, EndDate)
        VALUES (:medication_id, :time_of_day, :repeat_days, :start_date, :end_date);""")

    for t in times:
        db.execute(query, {
            "medication_id": medication_id,
            "time_of_day": t,       
            "repeat_days": repeat_days,
            "start_date": start_date,
            "end_date": end_date
        })