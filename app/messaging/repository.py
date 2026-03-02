from sqlalchemy import text
from sqlalchemy.engine import Connection

def get_relationship(conn: Connection, relationship_id: int):
    q = text("""SELECT RelationshipID, ElderID, CaregiverID
        FROM CareRelationships WHERE RelationshipID = :rid""")
    return conn.execute(q, {"rid": relationship_id}).mappings().first()

def validate_sender_and_get_receiver(conn: Connection, relationship_id: int, sender_id: int) -> int:
    rel = get_relationship(conn, relationship_id)
    if not rel:
        raise ValueError("Relationship not found")

    elder_id = rel["ElderID"]
    caregiver_id = rel["CaregiverID"]

    if sender_id != elder_id and sender_id != caregiver_id:
        raise PermissionError("Sender not in this relationship")

    return caregiver_id if sender_id == elder_id else elder_id

def insert_message(conn: Connection, relationship_id: int, sender_id: int, message_text: str) -> int:
    q = text("""INSERT INTO Messages (RelationshipID, SenderID, message_text, IsRead, SentAt)
        OUTPUT INSERTED.MessageID
        VALUES (:rid, :sid, :txt, 0, SYSDATETIME())""")
    mid = conn.execute(q, {"rid": relationship_id, "sid": sender_id, "txt": message_text}).scalar_one()
    return int(mid)

def list_messages(conn: Connection, relationship_id: int, after_id: int = 0, limit: int = 200):
    q = text("""SELECT TOP (:lim) MessageID, RelationshipID, SenderID, message_text, IsRead, SentAt
        FROM Messages
        WHERE RelationshipID = :rid AND MessageID > :after_id ORDER BY MessageID ASC""")
    return conn.execute(q, {"rid": relationship_id, "after_id": after_id, "lim": limit}).mappings().all()

def mark_messages_read(conn: Connection, relationship_id: int, message_ids: list[int]) -> int:
    if not message_ids:
        return 0

    # safe-enough for student project: force ints
    ids = ",".join(str(int(x)) for x in message_ids)

    q = text(f"""UPDATE Messages SET IsRead = 1
        WHERE RelationshipID = :rid
          AND MessageID IN ({ids})""")
    res = conn.execute(q, {"rid": relationship_id})
    return res.rowcount or 0

def get_user_fcm_token(conn: Connection, user_id: int) -> str | None:
    q = text("""SELECT FCMToken FROM UserDevices
        WHERE UserID = :uid""")
    row = conn.execute(q, {"uid": user_id}).mappings().first()
    return row["FCMToken"] if row and row.get("FCMToken") else None