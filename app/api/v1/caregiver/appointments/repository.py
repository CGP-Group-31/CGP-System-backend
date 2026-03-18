from sqlalchemy import text
from sqlalchemy.orm import Session
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
        OUTPUT INSERTED.AppointmentID AS id  
        VALUES(
            :elder_id, :doctor_name, :title, :location, :notes,
            :appointment_date, :appointment_time, GETDATE()
        )
    """)

    try:
        result = db.execute(query, {
            "elder_id": data.elder_id,
            "doctor_name": data.doctor_name,
            "title": data.title,
            "location": data.location,
            "notes": data.notes,
            "appointment_date": data.appointment_date,
            "appointment_time": data.appointment_time,
        })
        
        row = result.fetchone()
        appointment_id = row[0] if row else None

        return int(appointment_id) if appointment_id else None

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError(f"DB error while creating appointment: {str(e)}")


def update_appointment(db: Session, appointment_id: int, data):

    update_field = {}
    query_part = []

    if data.doctor_name is not None:
        query_part.append("DoctorName = :doctor_name")
        update_field["doctor_name"] = data.doctor_name

    if data.title is not None:
        query_part.append("Title = :title")
        update_field["title"] = data.title

    if data.notes is not None:
        query_part.append("Notes = :notes")
        update_field["notes"] = data.notes

    if data.location is not None:
        query_part.append("Location = :location")
        update_field["location"] = data.location

    if data.appointment_date is not None:
        query_part.append("AppointmentDate = :appointment_date")
        update_field["appointment_date"] = data.appointment_date

    if data.appointment_time is not None:
        query_part.append("AppointmentTime = :appointment_time")
        update_field["appointment_time"] = data.appointment_time

    if not query_part:
        return "no_fields"

    update_field["appointment_id"] = appointment_id

    set_clause = ", ".join(query_part)

    query = text("""
        UPDATE Appointments
        SET """ + set_clause + """
        WHERE AppointmentID = :appointment_id
    """)

    try:
        result = db.execute(query, update_field)
        return "updated" if result.rowcount > 0 else "not_found"

    except SQLAlchemyError as e:
        raise RuntimeError("DB error while updating appointments")


def delete_appointment(db: Session, appointment_id: int):
    query = text("""
        DELETE FROM Appointments WHERE AppointmentID = :appointment_id
    """)

    result = db.execute(query, {"appointment_id": appointment_id})
    return result.rowcount > 0


def upcoming_appointments(db: Session, elder_id: int):
    query = text("""
        SELECT *
        FROM Appointments
        WHERE ElderID = :elder_id
          AND AppointmentDate >= CAST(GETDATE() AS date)
          AND AppointmentDate < DATEADD(day, 7, CAST(GETDATE() AS date))
        ORDER BY AppointmentDate, AppointmentTime
    """)

    rows = db.execute(query, {"elder_id": elder_id}).mappings().all()
    return [dict(r) for r in rows]


def upsert_appointment_reminders(db: Session, appointment_id: int):

    row = db.execute(text("""
        SELECT AppointmentDate, AppointmentTime
        FROM Appointments
        WHERE AppointmentID = :aid
    """), {"aid": appointment_id}).fetchone()

    if not row:
        return False

    appt_dt = datetime.combine(row.AppointmentDate, row.AppointmentTime)
    appt_dt = appt_dt.replace(tzinfo=TZ)

    reminder_24h = appt_dt - timedelta(hours=24)
    reminder_6h = appt_dt - timedelta(hours=6)

    db.execute(text("""
        DELETE FROM AppointmentReminders WHERE AppointmentID = :aid
    """), {"aid": appointment_id})

    now = datetime.now(TZ)

    if reminder_24h > now:
        db.execute(text("""
            INSERT INTO AppointmentReminders (AppointmentID, ReminderType, ScheduledFor, Status)
            VALUES (:aid, '24H', :sf, 'PENDING')
        """), {"aid": appointment_id, "sf": reminder_24h})

    if reminder_6h > now:
        db.execute(text("""
            INSERT INTO AppointmentReminders (AppointmentID, ReminderType, ScheduledFor, Status)
            VALUES (:aid, '6H', :sf, 'PENDING')
        """), {"aid": appointment_id, "sf": reminder_6h})

    return True


def delete_appointment_reminders(db: Session, appointment_id: int):
    db.execute(text("""
        DELETE FROM AppointmentReminders WHERE AppointmentID = :aid
    """), {"aid": appointment_id})