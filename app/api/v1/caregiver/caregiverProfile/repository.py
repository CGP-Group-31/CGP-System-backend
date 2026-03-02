from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import SQLAlchemyError


def get_caregiver_profile(db: Session, caregiver_id: int):
    query = text("""
            SELECT UserID, FullName, Email, Phone, Address, DateOfBirth, Gender
            FROM Users
            WHERE UserID = :user_id AND RoleID = 4 AND IsActive = 1
        """)
    try:
        return db.execute(query,{"user_id":caregiver_id}).mappings().first()
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching caregiver profile") from e

   

def update_caregiver_profile(db: Session, caregiver_id: int, data):
    update_field ={}
    query_part=[]

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

    if data.password is not None:
        query_part.append("Password= :password")
        update_field["password"] = hash_password(data.password)

    if not query_part:
        return "no_fields"

    query = text(f"""
            UPDATE Users SET {', '.join(query_part)} 
            WHERE UserID= :user_id AND RoleID=4 AND IsActive= 1
            """)
    update_field["user_id"]= caregiver_id

    try:
        result = db.execute(query, update_field)
        return "updated" if result.rowcount >0 else "not_found"
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while updating caregiver profile") from e

    

def deactivate_account(db: Session, caregiver_id: int):
    query =text("""
            UPDATE Users SET IsActive = 0 WHERE UserID= :user_id
        """)
    try:
        result = db.execute(query,{"user_id": caregiver_id})
        return result.rowcount>0
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while deactivating caregiver") from e
    