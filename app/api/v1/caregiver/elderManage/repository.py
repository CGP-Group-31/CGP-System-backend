from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.encryption import decrypt_text

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
    query = text("""
            SELECT UserID, FullName, Email, Phone, Address, DateOfBirth, Gender
            FROM Users WHERE UserID= :user_id AND RoleID=5 AND IsActive=1
            """)
    try:
        return db.execute(query, {"user_id": elder_id}).mappings().first()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching elder details") from e


def get_elder_profile(db:Session, elder_id: int):
    query = text("""
            SELECT e.ElderID, e.BloodType, e.Allergies, e.ChronicConditions,
            e.EmergencyNotes, e.PastSurgeries, e.PreferredDoctorID, d.FullName AS DoctorName FROM ElderProfiles e
            LEFT JOIN Users d ON e.PreferredDoctorID=d.UserID AND d.RoleID=2 AND d.IsActive=1
            WHERE e.ElderID= :user_id 
        """)
    try:
        row = db.execute(query, {"user_id": elder_id}).mappings().first()
        if not row:
            return None
        
        data = dict(row)
        for key in ["Allergies", "ChronicConditions", "EmergencyNotes", "PastSurgeries"]:
            val = data.get(key)
            if val:
                try:
                    data[key] = decrypt_text(val)
                except Exception:
                    data[key]=val
        return data
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching elder profile") from e


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

    if data.email is not None:
        query_part.append("Email= :email")
        update_field["email"] = data.email.strip().lower()

    if not query_part:
        return "no_fields"

    query = text(f"""
            UPDATE Users SET {', '.join(query_part)} 
            WHERE UserID= :elder_id AND RoleID =5 AND IsActive=1
            """)
    update_field["elder_id"]= elder_id

    try:
        result=db.execute(query, update_field)
        return "updated" if result.rowcount>0 else "not_found"
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while updating elder details") from e



def get_preferred_doctor(db:Session, elder_id: int):
    query =text("""
            SELECT e.ElderID, e.PreferredDoctorID, d.FullName AS DoctorName FROM ElderProfiles e
            LEFT JOIN Users d ON e.PreferredDoctorID=d.UserID AND d.RoleID=2 AND d.IsActive=1
            WHERE e.ElderID= :user_id 
        """)
    try:
        row =   db.execute(query,{"user_id": elder_id}).mappings().first()
        if not row:
            return None
        
        return dict(row)
    
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching preferred doctor details") from e


def update_preferred_doctor(db:Session, elder_id: int, preferred_doc_id: int):
    query = text("""
            UPDATE ElderProfiles SET PreferredDoctorID =:preferred_doctor_id
            WHERE ElderID=:elder_id  
        """)
    try:
        row = db.execute(query,{"elder_id": elder_id,
              "preferred_doctor_id": preferred_doc_id
            })
        return "updated" if row.rowcount>0 else "not_found"
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while updating doctor details") from e
        