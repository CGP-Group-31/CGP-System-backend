# app/modules/medication/repository.py
from sqlalchemy import text
from sqlalchemy.orm import Session


def create_medication(db: Session, data) -> int:

    query = text("""
        INSERT INTO Medications 
        (ElderID, MedicationName, Dosage, Instructions, CreatedBy)
        OUTPUT INSERTED.MedicationID
        VALUES (:elder_id, :name, :dosage, :instructions, :created_by)
    """)

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
    times,
    repeat_days,
    start_date,
    end_date
):

    query = text("""
        INSERT INTO MedicationSchedules
        (MedicationID, TimeOfDay, RepeatDays, StartDate, EndDate)
        VALUES
        (:medication_id, :time_of_day, :repeat_days, :start_date, :end_date)
    """)

    for t in times:
        db.execute(query, {
            "medication_id": medication_id,
            "time_of_day": t,
            "repeat_days": repeat_days,
            "start_date": start_date,
            "end_date": end_date
        })


def get_medications_by_elder(db: Session, elder_id: int):

    query = text("""
        SELECT 
            m.MedicationID,
            m.MedicationName,
            m.Dosage,
            m.Instructions,
            s.TimeOfDay,
            s.RepeatDays,
            s.StartDate,
            s.EndDate
        FROM Medications m
        LEFT JOIN MedicationSchedules s
        ON m.MedicationID = s.MedicationID
        WHERE m.ElderID = :elder_id
        AND m.IsActive = 1
        ORDER BY s.TimeOfDay
    """)

    rows = db.execute(query, {"elder_id": elder_id}).fetchall()

    medications = {}

    for row in rows:

        med_id = row.MedicationID

        if med_id not in medications:
            medications[med_id] = {
                "medicationId": med_id,
                "name": row.MedicationName,
                "dosage": row.Dosage,
                "instructions": row.Instructions,
                "times": [],
                "repeatDays": row.RepeatDays if row.RepeatDays else "Daily",
                "startDate": row.StartDate,
                "endDate": row.EndDate
            }

        if row.TimeOfDay:
            medications[med_id]["times"].append(
                row.TimeOfDay.strftime("%H:%M")
            )

    return list(medications.values())


def update_medication(db: Session, medication_id: int, data):
    query = text("""
        UPDATE Medications
        SET
            MedicationName = :name,
            Dosage = :dosage,
            Instructions = :instructions
        WHERE MedicationID = :medication_id AND IsActive = 1""")

    result = db.execute(query, {
        "name": data.name,
        "dosage": data.dosage,
        "instructions": data.instructions,
        "medication_id": medication_id
    })

    if result.rowcount == 0:
        raise Exception("Medication not found or inactive")


def replace_medication_schedules(
    db: Session,
    medication_id: int,
    times,
    repeat_days,
    start_date,
    end_date
):
    delete_adherence_query = text("""
        DELETE ma
        FROM MedicationAdherence ma
        INNER JOIN MedicationSchedules ms
            ON ma.ScheduleID = ms.ScheduleID
        WHERE ms.MedicationID = :medication_id""")
    db.execute(delete_adherence_query, {"medication_id": medication_id})

    #  delete old schedules
    delete_schedules_query = text("""
        DELETE FROM MedicationSchedules
        WHERE MedicationID = :medication_id
    """)
    db.execute(delete_schedules_query, {"medication_id": medication_id})

    #  insert new schedules
    insert_query = text("""
        INSERT INTO MedicationSchedules
            (MedicationID, TimeOfDay, RepeatDays, StartDate, EndDate)
        VALUES
            (:medication_id, :time_of_day, :repeat_days, :start_date, :end_date)""")

    for t in times:
        db.execute(insert_query, {
            "medication_id": medication_id,
            "time_of_day": t,
            "repeat_days": repeat_days,
            "start_date": start_date,
            "end_date": end_date
        })

def deactivate_medication(db: Session, medication_id: int):

    query = text("""
        UPDATE Medications
        SET IsActive = 0
        WHERE MedicationID = :medication_id
    """)

    db.execute(query, {"medication_id": medication_id})