from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def get_chat_messages_by_elder(db: Session, elder_id: int, limit: int):
    try:
        elder_exists = db.execute(
            text("SELECT 1 FROM Users WHERE UserID = :elder_id"),
            {"elder_id": elder_id}
        ).scalar_one_or_none()

        if elder_exists is None:
            return None, "Elder not found."

        safe_limit = int(limit)

        rows = db.execute(
            text(f"""
                SELECT TOP {safe_limit}
                    MessageID,
                    ThreadID,
                    ElderID,
                    Role,
                    Content,
                    CreatedAt,
                    DetectedMoodID
                FROM ChatMessages
                WHERE ElderID = :elder_id
                ORDER BY CreatedAt DESC, MessageID DESC
            """),
            {"elder_id": elder_id}
        ).mappings().all()

        messages = []
        for row in rows:
            messages.append({
                "message_id": row["MessageID"],
                "thread_id": row["ThreadID"],
                "elder_id": row["ElderID"],
                "role": row["Role"],
                "content": row["Content"],
                "created_at": row["CreatedAt"],
                "detected_mood_id": row["DetectedMoodID"],
            })

        return messages, None

    except SQLAlchemyError:
        return None, "Database error occurred while fetching chat messages."