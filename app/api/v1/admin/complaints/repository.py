from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


GET_ALL_COMPLAINTS = text("""
    SELECT
        ComplaintID AS complaint_id,
        ComplainantID AS complainant_id,
        Subject AS subject,
        Description AS description,
        Status AS status,
        CreatedAt AS created_at
    FROM Complaints
    ORDER BY CreatedAt DESC, ComplaintID DESC
""")


def get_all_complaints(db):
    try:
        result = db.execute(GET_ALL_COMPLAINTS)
        return result.mappings().all(), None
    except SQLAlchemyError:
        return None, "Database error occurred while fetching complaints."