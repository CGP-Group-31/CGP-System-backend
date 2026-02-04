from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


ROLE_ELDER = 5

def create_elder(db: Session, data):
    query = text("""INSERT INTO Users (
            RoleID, FullName, Email, Phone, PasswordHash,
            DateOfBirth, Gender, IsActive, CreatedAt, LastLogin, Address)
        OUTPUT INSERTED.UserID
        VALUES (:role_id, :full_name, :email, :phone, :password,
            :dob, :gender, 1, GETDATE(), GETDATE(), :address)""")

    result = db.execute(
        query,
        {
            "role_id": ROLE_ELDER,
            "full_name": data.full_name,
            "email": data.email,
            "phone": data.phone,
            "password": hash_password(data.password),
            "dob": data.date_of_birth,
            "gender": data.gender,
            "address": data.address
        }
    )

    return result.scalar()


def create_relationship(db: Session, data):
    query = text("""INSERT INTO CareRelationships (
            ElderID, CaregiverID, RelationshipType, IsPrimary)
        OUTPUT INSERTED.RelationshipID
        VALUES (
            :elder_id, :caregiver_id, :relationship_type, :is_primary)""")

    result = db.execute(
        query,
        {
            "elder_id": data.elderID,
            "caregiver_id": data.caregiverTD,
            "relationship_type": data.RelationshipType,
            "is_primary": data.IsPrimary
        }
    )

    return result.scalar()
    
