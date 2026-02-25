from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def get_active_sos(db: Session, elder_id: int) ->dict| None:
    query = text("""
    SELECT TOP 1 SOSID, ElderID, TriggerTypeID, TriggerAt FROM SOSLogs
                 WHERE ElderID=:elder_id ORDER BY TriggeredAT DESC
    """)
    
    try:
        result = db.execute(query,{"elder_id": elder_id}).mappings().first()
        return dict(result) if result else None
    except SQLAlchemyError as e:
            raise RuntimeError("DB error while fetching active SOS") from e
    

def get_history_sos(db: Session, elder_id: int) ->dict| None:
    query = text("""
    SELECT SOSID, ElderID, TriggerTypeID, TriggerAt FROM SOSLogs
                 WHERE ElderID=:elder_id ORDER BY TriggeredAT DESC
    """)
    
    try:
        result = db.execute(query,{"elder_id": elder_id}).mappings().first()
        return dict(result) if result else None
    except SQLAlchemyError as e:
            raise RuntimeError("DB error while fetching active SOS") from e