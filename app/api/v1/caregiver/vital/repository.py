from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def list_vital_types(db: Session):
    q = text("""SELECT VitalTypeID, VitalName, Unit FROM VitalTypes ORDER BY VitalTypeID ASC""")
    return db.execute(q).mappings().all()

def create_vital_record(db: Session, elder_id: int, vital_type_id: int, value: float, notes: str | None, recorded_by: int):
    # SQL Server: OUTPUT INSERTED...
    q = text("""INSERT INTO VitalRecords (ElderID, VitalTypeID, Value, Notes, RecordedBy)
        OUTPUT INSERTED.RecordID, INSERTED.RecordedAt
        VALUES (:elder_id, :vital_type_id, :value, :notes, :recorded_by)""")
    row = db.execute(q, {
        "elder_id": elder_id,
        "vital_type_id": vital_type_id,
        "value": value,
        "notes": notes,
        "recorded_by": recorded_by
    }).mappings().first()
    return row  # {"RecordID": ..., "RecordedAt": ...}

def get_latest_vitals_by_type(db: Session, elder_id: int, limit_per_type: int):

    q = text("""WITH Ranked AS (SELECT vr.RecordID, vr.ElderID, vr.VitalTypeID, vt.VitalName, vt.Unit,
                vr.Value, vr.Notes, vr.RecordedBy, vr.RecordedAt,
                ROW_NUMBER() OVER (
                    PARTITION BY vr.VitalTypeID
                    ORDER BY vr.RecordedAt DESC) AS rn
            FROM VitalRecords vr
            JOIN VitalTypes vt ON vt.VitalTypeID = vr.VitalTypeID
            WHERE vr.ElderID = :elder_id)
        SELECT RecordID, ElderID, VitalTypeID, VitalName, Unit, Value, Notes, RecordedBy, RecordedAt
        FROM Ranked
        WHERE rn <= :limit_per_type
        ORDER BY VitalTypeID ASC, RecordedAt DESC""")
    rows = db.execute(q, {"elder_id": elder_id, "limit_per_type": limit_per_type}).mappings().all()
    return rows