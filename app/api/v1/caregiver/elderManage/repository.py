from sqlalchemy import text
from sqlalchemy.orm import Session


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
        update_field["full_name"] = data.full_name

    if data.phone is not None:
        query_part.append("Phone= :phone")
        update_field["phone"] = data.phone

    if data.address is not None:
        query_part.append("Address= :address")
        update_field["address"] = data.address

    if not query_part:
        return 

    query = f"""
            UPDATE Users SET {', '.join(query_part)} 
            WHERE UserID= :elder_id 
            """
    update_field["elder_id"]= elder_id
    result=db.execute(text(query), update_field)

    if result.rowcount == 0:
        return False
    return True


def update_elder_profile( db:Session, elder_id:int, data):
    update_field={}
    query_part = []

    if data.blood_type is not None:
        query_part.append("BloodType= :blood_type")
        update_field["blood_type"] = data.blood_type

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
        return None
    
    query = text(f"""
        UPDATE ElderProfiles SET {', '.join(query_part)}
        WHERE ElderID = :elder_id
    """)

    update_field["elder_id"]=elder_id

    result = db.execute(query, update_field)
    
    if result.rowcount == 0:
        return False
    return True


