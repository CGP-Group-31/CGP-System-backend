from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def get_caregiver_name(db:Session, caregiver_id:int) -> str|None:
    try:
        query = text("SELECT FullName FROM Users WHERE UserID =:caregiver_id AND RoleID = 4 AND IsActive=1")
        row= db.execute(query,{"caregiver_id": caregiver_id}).first()
        return row[0] if row else None

    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching username") from e



def missed_tdy_count(db: Session, elder_id: int)->int:
    query = text("""
    SELECT COUNT(*) AS cnt FROM MedicationAdherence WHERE ElderID=:elder_id
    AND CAST(ScheduledFor AS date) = CAST(GETDATE() AS date) AND StatusID = 4                 
""")
    
    try:
        row= db.execute(query,{"elder_id": elder_id}).mappings().first()
        return int(row["cnt"]) if row else 0
    
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching missed medication count") from e



def upcoming_appointment_count(db:Session, elder_id: int) -> int:
    query = text("""
        SELECT COUNT(*) AS cnt FROM Appointments WHERE ElderID=:elder_id AND
        AppointmentDate BETWEEN CAST(GETDATE() AS date) AND DATEADD(day, 7, CAST(GETDATE() AS date))
""")
    try:
        row = db.execute(query,{"elder_id": elder_id}).mappings().first()
        return int(row["cnt"]) if row else 0 
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching upcoming appointment count") from e







