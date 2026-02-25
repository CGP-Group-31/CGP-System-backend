from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

MISSED_STATUS_ID = 4
TAKEN_STATUS_ID = 2

base_select_query = """
            SELECT ma.AdherenceID, ma.ElderID, ma.ScheduleID, ma.ScheduledFor, ma.TakenAt, ma.StatusID,
            m.MedicationID, m.Dosage, m.MedicationName FROM MedicationAdherence ms INNER JOIN Medications m ON m.MedicationID = ms.MedicationID
            WHERE ma.ElderID =:elder_id AND CAST(ma.ScheduledFor AS date) = CAST(GETDATE() AS date)
"""


def get_all_scheduled(db: Session, elder_id: int):
    query = text(base_select_query)
    
    try:
        return db.execute(query,{"elder_id": elder_id}).mappings().all()
    
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching all medicine schedules") from e


def get_today_scheduled(db: Session, elder_id: int):
    query = text(base_select_query+" ORDER BY ma.ScheduledFor ASC")
    
    try:
        return db.execute(query,{"elder_id": elder_id}).mappings().all()
    
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching today's scheduled medicine") from e
    

def get_today_missed(db: Session, elder_id: int):
    query = text(base_select_query+" AND ma.StatusID=:status_id ORDER BY ma.ScheduledFor ASC")
    
    try:
        return db.execute(query,{"elder_id": elder_id, "status_id": MISSED_STATUS_ID}).mappings().all()
    
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching today's missed medicine") from e
    


def get_today_taken(db: Session, elder_id: int):
    query = text(base_select_query+" AND ma.StatusID=:status_id ORDER BY ma.TakenAt DESC")
    
    try:
        return db.execute(query,{"elder_id": elder_id, "status_id": TAKEN_STATUS_ID}).mappings().all()
    
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching today's taken medicine") from e