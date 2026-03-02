from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import SQLAlchemyError


def if_elder_exist(db:Session, elder_id: int):
    query = text("""
            SELECT 1 FROM Users WHERE UserID=:user_id AND RoleID=5 AND IsActive=1;
        """)
    try:
        return bool(db.execute(query, {"user_id": elder_id}).scalar())
    except SQLAlchemyError as e:
        raise RuntimeError("DB error while checking elder existence") from e



def get_elder_profile_with_primary_caregiver(db: Session, elder_id: int):
    query = text("""
            SELECT u.UserID, u.FullName AS ElderFullName, u.Email, u.Phone, u.Address, u.DateOfBirth, u.Gender, cr.CaregiverID, cu.FullName AS CaregiverFullName, cr.RelationshipType, cr.IsPrimary
            FROM Users u LEFT JOIN(SELECT TOP 1 * FROM CareRelationships WHERE ElderID=:elder_id ORDER BY IsPrimary DESC, RelationshipID DESC) cr 
            ON cr.ElderID = u.UserID LEFT JOIN Users cu ON cu.UserID = cr.CaregiverID AND cu.RoleID =4 AND cu.IsActive = 1
            WHERE u.UserID =:elder_id AND u.IsActive =1
            
        """)
    try:
        row = db.execute(query,{"elder_id":elder_id}).mappings().first()
        if not row: return None

        caregiver_ = None
        if row["CaregiverID"] is not None and row["CaregiverFullName"] is not None:
            caregiver_ = {
                "CaregiverID": int(row["CaregiverID"]),
                "CaregiverFullName" : row["CaregiverFullName"],
                "RelationshipType": row["RelationshipType"],
                "IsPrimary": bool(row["IsPrimary"]) if row["IsPrimary"] is not None else False,
            }


        return{
            "UserID": int(row["UserID"]),
            "ElderFullName": row["ElderFullName"],
            "Email": row["Email"],
            "Phone": row["Phone"],
            "DateOfBirth": row["DateOfBirth"],
            "Address": row["Address"],
            "Gender": row["Gender"],
            "caregiver": caregiver_,
        }

    except SQLAlchemyError as e:
        raise RuntimeError("DB error while fetching elder profile with caregiver") from e

   

