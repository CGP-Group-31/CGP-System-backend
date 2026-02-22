from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def create_vital_record(db: Session, data: dict):
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
                SELECT VitalTypeID, VitalName FROM VitalTypes 
                 """)
    try:
        return db.execute(query).mappings().all()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching existing vital") from e



def get_vitals(db: Session, elder_id: int):
    query = text("""
                SELECT RecordID, ElderID, VitalTypeID, Value, Notes FROM VitalRecords WHERE ElderID = :elder_id 
                 """)
    
    try:
        return db.execute(query, {"elder_id": elder_id}).mappings().first()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching vital data") from e



def update_vitals(db: Session, record_id: int, data: dict):
    update_field ={}
    query_part=[]


    if "vital_type_id" is not None:
        query_part.append("VitalTypeID= :vital_type_id")
        update_field["vital_type_id"] = data.vital_type_id

    if "title" is not None:
        query_part.append("Title= :title")
        update_field["title"] = data.title

    if "value" is not None:
        query_part.append("Value= :value")
        update_field["value"] = data.value

    if "notes" is not None:
        query_part.append("Notes= :notes")
        update_field["notes"] = data.notes

    if not query_part:
        return "no_fields"
    
    query = text(f"""
                UPDATE VitalRecords SET {', '.join(query_part)} 
                WHERE RecordID= :record_id 
                """)
    
    update_field["record_id"]= record_id

    try:
        result = db.execute(query, update_field)
        return "updated" if result.rowcount >0 else "not_found"
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while updating vitals") from e
