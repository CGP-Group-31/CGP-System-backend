from sqlalchemy import text
from sqlalchemy.orm import Session


def get_vitals_for_elder_in_range(db: Session, elder_id: int, start_dt, end_dt):
    q = text("""SELECT vr.RecordID, vr.ElderID, vt.VitalName, vt.Unit,
                vr.Value, vr.Notes, vr.RecordedAt
            FROM VitalRecords vr
            JOIN VitalTypes vt ON vt.VitalTypeID = vr.VitalTypeID
            WHERE vr.ElderID = :elder_id
              AND vr.RecordedAt >= :start_dt
              AND vr.RecordedAt < :end_dt
            ORDER BY vr.RecordedAt DESC""")
    rows = db.execute(q, {
        "elder_id": elder_id,
        "start_dt": start_dt,
        "end_dt": end_dt,
    }).mappings().all()
    return rows
