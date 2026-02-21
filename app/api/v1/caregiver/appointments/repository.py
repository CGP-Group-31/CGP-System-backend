from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError

def create_appointment(db: Session, data: dict):

    try:
        query= text("""
                INSERT INTO Appointments(ElderID, DoctorName, Title, Location, Notes, AppointmentDate, AppointmentTime, RecordedAt)
                VALUES(:elder_id, :doctor_name, :title, :location, :notes, :appointment_date, :appointment_time, GETDATE())
    """)
        
        db.execute(query, {
            "elder_id" : data.elder_id,
            "doctor_name" : data.doctor_name,
            "title" : data.title,
            "location" : data.location,
            "notes" : data.notes,
            "appointment_date" : data.appointment_date,
            "appointment_time" : data.appointment_time
        })
        db.commit()
    
    
    except SQLAlchemyError:
        db.rollback()
        raise



def get_all_appointments(db: Session, elder_id: int):
    query = text("""
                SELECT AppointmentID, ElderID, DoctorName, Title, Location, Notes, AppointmentDate, AppointmentTime FROM Appointments WHERE ElderID = :elder_id 
                ORDER BY AppointmentDate, AppointmentTime
                 """)
    result = db.execute(query, {"elder_id": elder_id})
    return result.mappings().all()



def get_one_appointment(db: Session, appointment_id: int):
    query = text("""
                SELECT AppointmentID, ElderID, DoctorName, Title, Location, Notes, AppointmentDate, AppointmentTime FROM Appointments WHERE AppointmentID = :appointment_id 
                 """)
    result = db.execute(query, {"appointment_id": appointment_id})
    return result.mappings().first()



def update_appointment(db: Session, appointment_id: int, data: dict):
    update_field ={}
    query_part=[]


    if "doctor_name" in data:
        query_part.append("DoctorName= :doctor_name")
        update_field["doctor_name"] = data["doctor_name"]

    if "title" in data:
        query_part.append("Title= :title")
        update_field["title"] = data["title"]

    if "location" in data:
        query_part.append("Location= :location")
        update_field["location"] = data["location"]

    if "appointment_date" in data:
        query_part.append("AppointmentDate= :appointment_date")
        update_field["appointment_date"] = data["appointment_date"]

    if "appointment_time" in data:
        query_part.append("AppointmentTime= :appointment_time")
        update_field["appointment_time"] = data["appointment_time"]

    if "location" in data:
        query_part.append("Location= :location")
        update_field["location"] = data["location"]

    if not query_part:
        return False

    update_field["appointment_id"]= appointment_id

    try:

        query = f"""
                UPDATE Appointments SET {', '.join(query_part)} 
                WHERE AppointmentID= :appointment_id 
                """
        
        result = db.execute(text(query), update_field)

        if result.rowcount == 0:
            db.rollback()
            return False
        
        db.commit()
        return True

    except SQLAlchemyError:
        db.rollback()
        raise



def delete_appointment(db: Session, appointment_id: int):

    try:
        result = db.execute(
            text("""
                DELETE FROM Appointments WHERE AppointmentID= :appointment_id
            """),
            {"appointment_id": appointment_id}
        )

        if result.rowcount == 0:
            db.rollback()
            return False
        
        db.commit()
        return True
    
    except SQLAlchemyError:
        db.rollback()
        raise
