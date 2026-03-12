from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


INSERT_COMPLAINT = text("""
    INSERT INTO Complaints (ComplainantID, Subject, Description)
    VALUES (:complainant_id, :subject, :description)
""")


def create_complaint(db, data):
    try:
        db.execute(INSERT_COMPLAINT, {
            "complainant_id": data.complainant_id,
            "subject": data.subject,
            "description": data.description
        })
        db.commit()
        return True, None

    except IntegrityError:
        db.rollback()
        return None, "Invalid complainant ID or complaint data."

    except SQLAlchemyError:
        db.rollback()
        return None, "Database error occurred while submitting complaint."