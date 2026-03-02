from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import SQLAlchemyError

def latest_location(db: Session, elder_id: int) -> dict|None:
    query = text("""
SELECT TOP 1 LocationID, ElderID, Latitude, Longitude, RecordedAt FROM LocationTrack WHERE ElderID=:elder_id
ORDER BY RecordedAt DESC, LocationID DESC;
""")
    
    try:
        row = db.execute(query,{"elder_id": elder_id}).mappings().first()
        return dict(row) if row else None
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching location") from e
    


def last_3_location(db: Session, elder_id: int):
    query = text("""
SELECT TOP 3 LocationID, ElderID, Latitude, Longitude, RecordedAt FROM LocationTrack WHERE ElderID=:elder_id
ORDER BY RecordedAt DESC, LocationID DESC;
""")
    
    try:
        row = db.execute(query,{"elder_id": elder_id}).mappings().all()
        return row if row else None
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching location history") from e
