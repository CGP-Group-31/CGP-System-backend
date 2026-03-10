from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Colombo")

def create_appointment(db: Session, data):
    query = text("""
        INSERT INTO Appointments(
            ElderID, DoctorName, Title, Location, Notes,
            AppointmentDate, AppointmentTime, RecordedAt
        )
        OUTPUT INSERTED.AppointmentID
        VALUES(
            :elder_id, :doctor_name, :title, :location, :notes,
            :appointment_date, :appointment_time, GETDATE()
        )
    """)

    try:
        appointment_id = db.execute(query, {
            "elder_id": data.elder_id,
            "doctor_name": data.doctor_name,
            "title": data.title,
            "location": data.location,
            "notes": data.notes,
            "appointment_date": data.appointment_date,
            "appointment_time": data.appointment_time,
        }).scalar()

        return int(appointment_id) if appointment_id else None

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError("DB error while creating appointment") from e
    


def get_all_appointments(db: Session, elder_id: int):
    query = text("""
                SELECT AppointmentID, ElderID, DoctorName, Title, Location, Notes, AppointmentDate, AppointmentTime FROM Appointments WHERE ElderID = :elder_id 
                ORDER BY AppointmentDate, AppointmentTime
                 """)
    try:
        row = db.execute(query, {"elder_id": elder_id}).mappings().all()
        return [dict(r) for r in row]
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching appointments") from e


def update_appointment(db: Session, appointment_id: int, data):
    update_field ={}
    query_part=[]


    if data.doctor_name is not None:
        query_part.append("DoctorName= :doctor_name")
        update_field["doctor_name"] = data.doctor_name

    if data.title is not None:
        query_part.append("Title= :title")
        update_field["title"] = data.title

    if data.notes is not None:
        query_part.append("Notes = :notes")
        update_field["notes"] = data.notes

    if data.location is not None:
        query_part.append("Location= :location")
        update_field["location"] = data.location

    if data.appointment_date is not None:
        query_part.append("AppointmentDate= :appointment_date")
        update_field["appointment_date"] = data.appointment_date

    if data.appointment_time is not None:
        query_part.append("AppointmentTime= :appointment_time")
        update_field["appointment_time"] = data.appointment_time

    if not query_part:
        return "no_fields"

    update_field["appointment_id"]= appointment_id

    query = text(f"""
                UPDATE Appointments SET {', '.join(query_part)} 
                WHERE AppointmentID= :appointment_id 
                """)
    try:
        
        result = db.execute(query, update_field)
        return "updated" if result.rowcount >0 else "not_found"
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while updating appointments") from e



def delete_appointment(db: Session, appointment_id: int):
        query =text("""
                DELETE FROM Appointments WHERE AppointmentID= :appointment_id
            """)
        try:
            result = db.execute(query,{"appointment_id": appointment_id})
            return result.rowcount>0
        except SQLAlchemyError as e:
            raise RuntimeError("DB error while deleting appointment") from e
        

def upcoming_appointments(db: Session, elder_id: int):
    query = text("""
        SELECT
            AppointmentID,
            ElderID,
            DoctorName,
            Title,
            Location,
            Notes,
            AppointmentDate,
            AppointmentTime
        FROM Appointments
        WHERE ElderID = :elder_id
          AND AppointmentDate >= CAST(GETDATE() AS date)
          AND AppointmentDate < DATEADD(day, 7, CAST(GETDATE() AS date))
        ORDER BY AppointmentDate ASC, AppointmentTime ASC
    """)
    try:
        row = db.execute(query, {"elder_id": elder_id}).mappings().all()
        return [dict(r) for r in row]
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching upcoming appointments") from e


def upsert_appointment_reminders(db: Session, appointment_id: int):
    """
    Deletes existing reminders and creates fresh 24H and 6H reminder rows.
    """
    # fetch appointment datetime
    row = db.execute(text("""
        SELECT AppointmentDate, AppointmentTime
        FROM Appointments
        WHERE AppointmentID = :aid
    """), {"aid": appointment_id}).fetchone()

    if not row:
        return False

    appt_dt = datetime.combine(row.AppointmentDate, row.AppointmentTime).replace(tzinfo=TZ)

    reminder_24h = appt_dt - timedelta(hours=24)
    reminder_6h = appt_dt - timedelta(hours=6)

    # delete old reminders
    db.execute(text("""
        DELETE FROM AppointmentReminders WHERE AppointmentID = :aid
    """), {"aid": appointment_id})

    # insert new reminders ONLY if scheduled time is still in future
    now = datetime.now(TZ)

    to_insert = []
    if reminder_24h > now:
        to_insert.append(("24H", reminder_24h))
    if reminder_6h > now:
        to_insert.append(("6H", reminder_6h))

    for rtype, sched_for in to_insert:
        db.execute(text("""
            INSERT INTO AppointmentReminders (AppointmentID, ReminderType, ScheduledFor, Status)
            VALUES (:aid, :rtype, :sf, 'PENDING')
        """), {"aid": appointment_id, "rtype": rtype, "sf": sched_for})

    return True


def delete_appointment_reminders(db: Session, appointment_id: int):
    db.execute(text("""
        DELETE FROM AppointmentReminders WHERE AppointmentID = :aid
    """), {"aid": appointment_id})