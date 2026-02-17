from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def create_vital_record(db: Session, data: dict):

    query = text("""
        INSERT INTO VitalRecords (ElderID, VitalTypeID, Value, Notes, RecordedBy)
        VALUES (:elder_id, :vital_type_id, :value, :notes, :recorded_by);
        
        SELECT SCOPE_IDENTITY() AS RecordID;
    """)
    
    inserted_ids = []

    try:

        result1 = db.execute(query, {"elder_id": data["elder_id"], "vital_type_id": data["vital_type_id"],
                "value":data["value1"], "notes":data.get("notes"), "recorded_by": data["recorded_by"]
        })
    
        recorded_id1 = result1.fetchone()[0]
        inserted_ids.append(recorded_id1)

        if data.get("value2") is not None:
            result2 = db.execute(query, {"elder_id": data["elder_id"], "vital_type_id": data["vital_type_id"],
                "value":data["value2"], "notes":data.get("notes"), "recorded_by": data["recorded_by"]
        })
        
        recorded_id2 = result2.fetchone()[0]
        inserted_ids.append(recorded_id2)


        db.commit()
        return inserted_ids


    except SQLAlchemyError:
        db.rollback()
        raise