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
            d.Specialization AS specialization,
            d.Hospital AS hospital FROM Doctor d
        JOIN Users u ON u.UserID = d.DoctorID WHERE u.IsActive = 1 AND u.RoleID = :role_id""")

    result = db.execute(query, {"role_id": ROLE_DOCTOR})
    return result.mappings().all()


# def unset_primary_contact(db: Session, elder_id: int):
#     db.execute(
#         text("""UPDATE EmergencyContacts SET IsPrimary = 0 WHERE ElderID = :elder_id"""),
#         {"elder_id": elder_id}
#     )

# not sure the is primry state will be changed, when add a new contact is thatis not primary, check
# if the api returns the primary contact true only the UPDATE EmergencyContacts SET IsPrimary = 0
# if not not want to add a promary contact 
def create_emergency_contact(db: Session, data):
    if data.is_primary:
        db.execute(text("""UPDATE EmergencyContacts SET IsPrimary = 0 WHERE ElderID = :elder_id"""),
            {"elder_id": data.elder_id})

    db.execute(
        text("""INSERT INTO EmergencyContacts (ElderID, ContactName, Phone, Relationship, IsPrimary)
            VALUES (:elder_id, :contact_name, :phone, :relationship, :is_primary)"""),
        data.dict()
    )
    db.commit()



def get_emergency_contacts(db: Session, elder_id: int):
    result = db.execute(
        text("""SELECT ContactID, ElderID, ContactName, Phone, Relationship, IsPrimary
            FROM EmergencyContacts WHERE ElderID = :elder_id"""),
        {"elder_id": elder_id}
    )

    return result.mappings().all()


def search_doctors(
    db: Session,
    doctor_name: Optional[str] = None,
    hospital: Optional[str] = None
):
    query = """SELECT  d.DoctorID AS doctor_id, u.FullName AS full_name,
            d.Specialization AS specialization, d.Hospital AS hospital
        FROM Doctor d
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