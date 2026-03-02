from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .schemas import VitalCreate, VitalResponse

def create_vital_record(db: Session, data: VitalCreate):
        query = text("""
            INSERT INTO VitalRecords (ElderID, VitalTypeID, Value, Notes, RecordedBy, RecordedAt)
            VALUES (:elder_id, :vital_type_id, :value, :notes, :caregiver_id, GETDATE());  
        """)
        try:
            result= db.execute(query, {
                "elder_id": data.elder_id,
                "vital_type_id" : data.vital_type_id,
                "value" : data.value,
                "notes" :data.notes,
                "caregiver_id": data.caregiver_id
            })

            return result.rowcount >0
        
        except SQLAlchemyError as e:
            db.rollback()
            raise RuntimeError("DB error while creating vitals") from e



def all_vital_types(db: Session):
    query = text("""
                SELECT VitalTypeID, VitalName, Unit FROM VitalTypes 
                 """)
    try:
        return db.execute(query).mappings().all()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching existing vital") from e



def get_vitals(db: Session, elder_id: int) -> dict:
    query = text("""
                SELECT vt.VitalTypeID, vt.VitalName, vt.Unit FROM VitalTypes vt OUTER APPLY(SELECT TOP 1 RecordID, ElderID, Value, Notes, RecordedAt FROM VitalRecords vr WHERE ElderID = :elder_id AND 
                vr.VitalTypeID = vt.VitalTypeID ORDER BY vr.RecordedAt DESC, vr.RecordID DESC) vr2 ORDER BY vt.VitalName;
                 """)
    
    try:
        row =  db.execute(query, {"elder_id": elder_id}).mappings().all()
        if not row:
            return {}
        result: dict={}

        for r in row:
            vital_name= r["VitalName"]
            if r["RecordID"] is None:
                result[vital_name] = None
                continue
            result[vital_name]= {
                "record_id": int(r["RecordID"]),
                "vital_type_id": int(r["VitalTypeID"]),
                "value": float(r["Value"]),
                "unit": r["Unit"],
                "notes": r["Notes"],
                "recorded_at": r["RecordedAt"]
            }

        return result

    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching vital data") from e



