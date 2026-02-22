from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def if_caregiver_has_access_to_elder(db: Session, caregiver_id: int, elder_id: int):
    query = text("""
            SELECT 1 FROM CareRelationships cr
            JOIN Users c ON c.UserID=cr.CaregiverID
            JOIN Users e ON e.UserID=cr.ElderID
            WHERE cr.ElderID = :elder_id AND cr.CaregiverID= :caregiver_id
            AND (c.RoleID = 4 AND c.IsActive =1) AND (e.RoleID= 5 AND e.IsActive=1);
        """)
    try:
        return bool(db.execute(query, {"caregiver_id": caregiver_id, "elder_id": elder_id}).scalar())
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while checking caregiver access") from e
    

    
def if_elder_exist(db:Session, elder_id: int):
    query = text("""
            SELECT 1 FROM Users WHERE UserID = :user_id AND RoleID = 5 AND IsActive =1;
        """)
    try:
        return bool(db.execute(query, {"user_id": elder_id}).scalar())
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while checking elder existence") from e




def get_elder(db:Session, elder_id: int):
    return db.execute(
        text("""
            SELECT UserID, FullName, Email, Phone,Address, DateOfBirth, Gender
            FROM Users WHERE UserID= :user_id AND RoleID=5 AND IsActive=1
            """),{"user_id": elder_id}
    ).mappings().first()


def get_elder_profile(db:Session, elder_id: int):
    return db.execute(
        text("""
            SELECT ElderID, BloodType, Allergies, ChronicConditions,
            EmergencyNotes, PastSurgeries, PreferredDoctorID FROM ElderProfiles WHERE ElderID= :user_id 
        """),{"user_id": elder_id}).mappings().first()



def update_elder(db: Session, elder_id: int, data):
    update_field = {}
    query_part = []

    if data.full_name is not None:
        query_part.append("FullName= :full_name")
        update_field["full_name"] = data.full_name.strip()

    if data.phone is not None:
        query_part.append("Phone= :phone")
        update_field["phone"] = data.phone.strip()

    if data.address is not None:
        query_part.append("Address= :address")
        update_field["address"] = data.address.strip()

    if not query_part:
        return "no_fields"

    query = text(f"""
            UPDATE Users SET {', '.join(query_part)} 
            WHERE UserID= :elder_id AND RoleID =5 AND IsActive=1
            """)
    update_field["elder_id"]= elder_id
    result=db.execute(query, update_field)

    return "updated" if result.rowcount>0 else "not_found"


def update_elder_profile( db:Session, elder_id:int, data):
    update_field={}
    query_part = []

    if data.blood_type is not None:
        query_part.append("BloodType= :blood_type")
        update_field["blood_type"] = data.blood_type.strip()

    if data.allergies is not None:
        query_part.append("Allergies= :allergies")
        update_field["allergies"] = data.allergies

    if data.chronic_conditions is not None:
        query_part.append("ChronicConditions= :chronic")
        update_field["chronic"] = data.chronic_conditions

    if data.emergency_notes is not None:
        query_part.append("EmergencyNotes= :emergency_notes")
        update_field["emergency_notes"] = data.emergency_notes

    if data.past_surgeries is not None:
        query_part.append("PastSurgeries= :past_surgeries")
        update_field["past_surgeries"] = data.past_surgeries

    if data.preferred_doctor_id is not None:
        query_part.append("PreferredDoctorID= :preferred_docID")
        update_field["preferred_docID"] = data.preferred_doctor_id

    if not update_field:
        return "no_fields"
    
    query = text(f"""
        UPDATE ElderProfiles SET {', '.join(query_part)}
        WHERE ElderID = :elder_id
    """)

    update_field["elder_id"]=elder_id

    result = db.execute(query, update_field)
    
    return "updated" if result.rowcount>0 else "not_found"


