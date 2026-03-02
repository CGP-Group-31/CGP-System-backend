from sqlalchemy import text
from sqlalchemy.orm import Session

def create_sos_log(
    db: Session,
    elder_id: int,
    relationship_id: int,
    trigger_type_id: int,
):
    q = text("""
        INSERT INTO SOSLogs (ElderID, TriggerTypeID, RelationshipID)
        OUTPUT INSERTED.SOSID, INSERTED.TriggeredAt
        VALUES (:elder_id, :trigger_type_id, :relationship_id)""")
    row = db.execute(q, {
        "elder_id": elder_id,
        "trigger_type_id": trigger_type_id,
        "relationship_id": relationship_id,
    }).mappings().first()

    return row  

