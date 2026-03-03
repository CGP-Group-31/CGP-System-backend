from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def get_caregiver_name(db:Session, caregiver_id:int) -> str|None:
    try:
        query = text("SELECT FullName FROM Users WHERE UserID =:caregiver_id AND RoleID = 4 AND IsActive=1")
        row= db.execute(query,{"caregiver_id": caregiver_id}).first()
        return row[0] if row else None

    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching username") from e



def missed_tdy_count(db: Session, elder_id: int)->int:
    query = text("""
    SELECT COUNT(*) AS cnt FROM MedicationAdherence WHERE ElderID=:elder_id
    AND CAST(ScheduledFor AS date) = CAST(GETDATE() AS date) AND StatusID = 4                 
""")
    
    try:
        row= db.execute(query,{"elder_id": elder_id}).mappings().first()
        return int(row["cnt"]) if row else 0
    
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching missed medication count") from e



def upcoming_appointment_count(db:Session, elder_id: int) -> int:
    query = text("""
        SELECT COUNT(*) AS cnt FROM Appointments WHERE ElderID=:elder_id AND
        AppointmentDate BETWEEN CAST(GETDATE() AS date) AND DATEADD(day, 7, CAST(GETDATE() AS date))
""")
    try:
        row = db.execute(query,{"elder_id": elder_id}).mappings().first()
        return int(row["cnt"]) if row else 0 
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching upcoming appointment count") from e


def get_dashboard_home(db: Session, elder_id: int, caregiver_id: int) -> dict:
    name = get_caregiver_name(db, caregiver_id)
    if not name:
        return {"ok": False, "error": "Caregiver not found"}
    
    missed = missed_tdy_count(db, elder_id)
    upcoming = upcoming_appointment_count(db, elder_id)

    alerts = []
    if missed > 0:
        alerts.append({
            "title": "Missed Medicine",
            "subtitle": f"{missed} missed dose(s) today",
            "type": "missed_medicine",
        })
    if upcoming > 0:
        alerts.append({
            "title": "Upcoming Appointment",
            "subtitle": f"{upcoming} appointment(s) in next 7 days",
            "type": "upcoming_appointment",
        })

    #if there is nothing
    if not alerts:
        alerts.append({
            "title": "All Good!",
            "subtitle": "No urgent alerts right now",
            "type": "ok",
        })

    return {
        "ok": True,
        "elder_id": elder_id,
        "caregiver_id": caregiver_id,
        "caregiver_name": name,
        "missed_medication_today": missed,
        "upcoming_appointments_7_days": upcoming,
        "quick_alerts": alerts,
    }