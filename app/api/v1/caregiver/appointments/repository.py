from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError

def create_appointment(db: Session, data):
        query= text("""
                INSERT INTO Appointments(ElderID, DoctorName, Title, Location, Notes, AppointmentDate, AppointmentTime, RecordedAt)
                VALUES(:elder_id, :doctor_name, :title, :location, :notes, :appointment_date, :appointment_time, GETDATE())
    """)
        
        try:
            result = db.execute(query, {
            "elder_id" : data.elder_id,
            "doctor_name" : data.doctor_name,
            "title" : data.title,
            "location" : data.location,
            "notes" : data.notes,
            "appointment_date" : data.appointment_date,
            "appointment_time" : data.appointment_time
            })

            return result.rowcount >0
        
        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError("DB error while creating appointmnet") from e
    


def get_all_appointments(db: Session, elder_id: int):
    query = text("""
                SELECT AppointmentID, ElderID, DoctorName, Title, Location, Notes, AppointmentDate, AppointmentTime FROM Appointments WHERE ElderID = :elder_id 
                ORDER BY AppointmentDate, AppointmentTime
                 """)
    try:
        return db.execute(query, {"elder_id": elder_id}).mappings().all()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching appointments") from e


def get_one_appointment(db: Session, appointment_id: int):
    query = text("""
                SELECT AppointmentID, ElderID, DoctorName, Title, Location, Notes, AppointmentDate, AppointmentTime FROM Appointments WHERE AppointmentID = :appointment_id 
                 """)
    try:
        return db.execute(query, {"appointment_id": appointment_id}).mappings().first()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching an appointment") from e



def update_appointment(db: Session, appointment_id: int, data: dict):
    update_field ={}
    query_part=[]


    if "doctor_name" is not None:
        query_part.append("DoctorName= :doctor_name")
        update_field["doctor_name"] = data.doctor_name

    if "title" is not None:
        query_part.append("Title= :title")
        update_field["title"] = data.title

    if "location" is not None:
        query_part.append("Location= :location")
        update_field["location"] = data.location

    if "appointment_date" is not None:
        query_part.append("AppointmentDate= :appointment_date")
        update_field["appointment_date"] = data.appointment_date

    if "appointment_time" is not None:
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
        