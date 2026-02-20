from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password

def get_caregiver_profile(db: Session, caregiver_id: int):
    result = db.execute(
        text("""
            SELECT UserID, FullName, Email, Phone, Address, DateOfBirth, Gender
            FROM Users
            WHERE UserID = :user_id AND RoleID = 4 AND IsActive = 1
        """), {"user_id":caregiver_id}
    ).mappings().first()

    return result

def update_caregiver_profile(db: Session, caregiver_id: int, data):
    update_field ={}
    query_part=[]

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
        return None

    query = f"""
            UPDATE Users SET {', '.join(query_part)} 
            WHERE UserID= :user_id AND RoleID=4
            """
    update_field["user_id"]= caregiver_id
    result = db.execute(text(query), update_field)

    if result.rowcount == 0:
        return False
    return True

    


#password update..?

def deactivate_account(db: Session, caregiver_id: int):
    db.execute(
        text("""
            UPDATE Users SET IsActive = 0 WHERE UserID= :user_id
        """),
        {"user_id": caregiver_id}
    )