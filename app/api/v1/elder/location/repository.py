from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import SQLAlchemyError

def share_location(db: Session, data):
    query = text("""
INSERT INTO LocationTrack (ElderID, Latitude, Longitude) 
VALUES (:elder_id, :lat, :lng);
""")
    
    try:
        row = db.execute(query,{"elder_id": data.elder_id, "lat": data.latitude, "lng":data.longitude})
        return row.rowcount > 0
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while sharing location") from e
    


