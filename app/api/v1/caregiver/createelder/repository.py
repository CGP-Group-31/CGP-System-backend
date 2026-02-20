from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional
ROLE_DOCTOR =  2
ROLE_ELDER = 5
def create_elder(db: Session, data):
    query = text("""INSERT INTO Users (RoleID, FullName, Email, Phone, PasswordHash,
            DateOfBirth, Gender, IsActive, CreatedAt, LastLogin, Address)
        OUTPUT INSERTED.UserID
        VALUES (:role_id, :full_name, :email, :phone, :password,
            :dob, :gender, 1, GETDATE(), GETDATE(), :address)""")

    result = db.execute(query, {
        "role_id": ROLE_ELDER,
        "full_name": data.full_name,
        "email": data.email,
        "phone": data.phone,
        "password": hash_password(data.password),
        "dob": data.date_of_birth,
        "gender": data.gender,
        "address": data.address
    })

    return result.scalar()

def create_relationship(
    db: Session,
    elder_id: int,
    caregiver_id: int,
    relationship_type: str,
    is_primary: bool
):
    query = text("""INSERT INTO CareRelationships (ElderID, CaregiverID, RelationshipType, IsPrimary)
        OUTPUT INSERTED.RelationshipID
        VALUES (:elder_id, :caregiver_id, :relationship_type, :is_primary)""")

    result = db.execute(query, {
        "elder_id": elder_id,
        "caregiver_id": caregiver_id,
        "relationship_type": relationship_type,
        "is_primary": is_primary
    })

    return result.scalar()

    #later hash data without ElderID, PreferredDoctorID
def add_elder_records(db: Session, elder_id: int, data):
    query = text("""INSERT INTO ElderProfiles (ElderID, BloodType, Allergies, ChronicConditions,
            EmergencyNotes, PastSurgeries, PreferredDoctorID)
        OUTPUT INSERTED.ElderProfileID
        VALUES (:elder_id, :blood_type, :allergies, :chronic_conditions, :emergency_notes, :past_surgeries, :preferred_doctor_id)""")

    result = db.execute(query, {
        "elder_id": elder_id,
        "blood_type": data.blood_type,
        "allergies": data.allergies,
        "chronic_conditions": data.chronic_conditions,
        "emergency_notes": data.emergency_notes,
        "past_surgeries": data.past_surgeries,
        "preferred_doctor_id": data.preferred_doctor_id
    })

    return result.scalar()

ROLE_DOCTOR = 2  

def all_doctors(db: Session):
    query = text("""SELECT d.DoctorID AS doctor_id, u.FullName AS full_name,
            d.Specialization AS specialization, d.Hospital AS hospital FROM Doctor d
        JOIN Users u ON u.UserID = d.DoctorID WHERE u.IsActive = 1 AND u.RoleID = :role_id""")

    result = db.execute(query, {"role_id": ROLE_DOCTOR})
    return result.mappings().all()


CHECK_ELDER_EXISTS = text("""SELECT 1 FROM Users WHERE UserID = :elder_id AND IsActive = 1""")

INSERT_CONTACT = text("""INSERT INTO EmergencyContacts (ElderID, ContactName, Phone, Relationship, IsPrimary)
    OUTPUT INSERTED.ContactID
    VALUES (:elder_id, :contact_name, :phone, :relationship, :is_primary)""")

UNSET_PRIMARY = text("""UPDATE EmergencyContacts
    SET IsPrimary = 0 WHERE ElderID = :elder_id AND IsPrimary = 1""")

SELECT_CONTACTS = text("""SELECT ContactID AS contact_id, ElderID AS elder_id, ContactName AS contact_name, Phone AS phone,  Relationship AS relationship,
        IsPrimary AS is_primary FROM EmergencyContacts WHERE ElderID = :elder_id
    ORDER BY IsPrimary DESC, ContactID DESC""")


def create_emergency_contact(db: Session, data):
    try:
        exists = db.execute(CHECK_ELDER_EXISTS, {"elder_id": data.elder_id}).scalar()
        if not exists:
            return None, "Elder not found or inactive."

        if data.is_primary:
            db.execute(UNSET_PRIMARY, {"elder_id": data.elder_id})

        result = db.execute(INSERT_CONTACT, {
            "elder_id": data.elder_id,
            "contact_name": data.contact_name.strip(),
            "phone": data.phone.strip(),
            "relationship": data.relationship.strip(),
            "is_primary": 1 if data.is_primary else 0
        })

        contact_id = result.scalar()
        db.commit()
        return contact_id, None

    except IntegrityError as e:
        db.rollback()
        return None, "Database integrity error. Check ElderID and constraints."

    except SQLAlchemyError:
        db.rollback()
        return None, "Database error occurred while creating the emergency contact."

def get_emergency_contacts(db: Session, elder_id: int):
    try:
        result = db.execute(SELECT_CONTACTS, {"elder_id": elder_id})
        return result.mappings().all(), None
    except SQLAlchemyError:
        return None, "Database error occurred while fetching emergency contacts."

def search_doctors(
    db: Session,
    doctor_name: Optional[str] = None,
    hospital: Optional[str] = None):
    query = """SELECT  d.DoctorID AS doctor_id, u.FullName AS full_name, d.Specialization AS specialization, d.Hospital AS hospital FROM Doctor d
        JOIN Users u ON u.UserID = d.DoctorID WHERE u.IsActive = 1 AND u.RoleID = :role_id """

    params = {"role_id": ROLE_DOCTOR}

    if doctor_name:
        query += " AND u.FullName LIKE :doctor_name"
        params["doctor_name"] = f"%{doctor_name}%"

    if hospital:
        query += " AND d.Hospital LIKE :hospital"
        params["hospital"] = f"%{hospital}%"

    result = db.execute(text(query), params)
    return result.mappings().all()