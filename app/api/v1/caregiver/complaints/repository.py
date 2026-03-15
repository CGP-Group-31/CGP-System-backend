from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

CHECK_USER_EXISTS = text("""
    SELECT 1
    FROM Users
    WHERE UserID = :complainant_id
""")

INSERT_COMPLAINT = text("""
    INSERT INTO Complaints (ComplainantID, Subject, Description)
    VALUES (:complainant_id, :subject, :description)
""")


def create_complaint(db, data):
    try:
        user_exists = db.execute(
            CHECK_USER_EXISTS,
            {"complainant_id": data.complainant_id}
        ).scalar()

        if not user_exists:
            return None, "Complainant does not exist."

        db.execute(INSERT_COMPLAINT, {
            "complainant_id": data.complainant_id,
            "subject": data.subject,
            "description": data.description
        })
        db.commit()
        return True, None

    except IntegrityError:
        db.rollback()
        return None, "Invalid complaint data."

    except SQLAlchemyError:
        db.rollback()
        return None, "Database error occurred while submitting complaint."