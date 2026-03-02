from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def caregiver_owns_elder(db: Session, caregiver_id: int, elder_id: int) -> bool:
    try:
        return db.execute(text("""
        SELECT 1 FROM CareRelationships WHERE CaregiverID= :caregiver_id AND ElderID= :elder_id
"""),{"caregiver_id": caregiver_id, "elder_id": elder_id}).first() is not None
    
    except SQLAlchemyError as e:
        raise RecursionError("DB error while checking caregiver and elder ownership") from e



def get_relationship_id(db:Session, caregiver_id: int, elder_id:int) ->int |None:
    try:
        row = db.execute(text("""
        SELECT TOP 1 RelationshipID FROM CareRelationships WHERE 
        CaregiverID=:caregiver_id AND ElderID =:elder_id ORDER BY IsPrimary DESC, RelationshipID DESC
        """),{"caregiver_id":caregiver_id, "elder_id": elder_id}).first()
        return int(row[0]) if row else None
    
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching relationship id") from e



def if_caregiver_exist(db:Session, caregiver_id: int) -> bool:
    query = text("""
            SELECT 1 FROM Users WHERE UserID =:user_id AND RoleID = 4 AND IsActive =1;
        """)
    try:
        return db.execute(query, {"user_id": caregiver_id}).first() is not None
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while checking caregiver existence") from e
    



def if_elder_exist(db:Session, elder_id: int) -> bool:
    query = text("""
            SELECT 1 FROM Users WHERE UserID =:user_id AND RoleID = 5 AND IsActive =1;
        """)
    try:
        return db.execute(query, {"user_id": elder_id}).first() is not None
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while checking elder existence") from e