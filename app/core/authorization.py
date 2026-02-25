from sqlalchemy.orm import Session
from sqlalchemy import text

def caregiver_owns_elder(db: Session, caregiver_id: int, elder_id: int) -> bool:
    return db.execute(text("""
        SELECT 1 FROM CareRelationship WHERE CaregiverID= :caregiver_id AND ElderID= :elder_id
"""),{"caregiver_id": caregiver_id, "elder_id": elder_id}).first() is not None

def get_relationship_id(db:Session, caregiver_id: int, elder_id:int) ->int |None:
    row = db.execute(text("""
    SELECT TOP 1 RelationshipID FROM CareRelationships WHERE 
    CaregiverID=:caregiver_id AND ElderID =:elder_id ORDER BY IsPrimary DESC
    """),{"ciaregiver_d":caregiver_id, "elder_id": caregiver_id}).first()
    return int(row[0]) if row else None