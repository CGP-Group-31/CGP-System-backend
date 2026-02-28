from fastapi import APIRouter, HTTPException
from sqlalchemy import Engine
from app.core.database import get_db
from app.messaging.schemas import SendMessageIn, MessagesListOut, MessageOut, MarkReadIn
from app.messaging import repository as crud
from app.services.fcm_service import send_push_notification  
router = APIRouter(prefix="/api/messages", tags=["Messages"])

@router.post("/send", response_model=dict)
def send_message(payload: SendMessageIn):
    try:
        with get_db.begin() as conn:
            receiver_id = crud.validate_sender_and_get_receiver(
                conn, payload.relationship_id, payload.sender_id
            )

            message_id = crud.insert_message(
                conn, payload.relationship_id, payload.sender_id, payload.message_text
            )

            token = crud.get_user_fcm_token(conn, receiver_id)

        # Send FCM AFTER DB commit
        if token:
            try:
                send_push_notification(
                    token=token,
                    title="New Message",
                    body="Tap to listen",
                    data={
                        "type": "chat_message",
                        "relationship_id": payload.relationship_id,
                        "message_id": message_id,
                        "sender_id": payload.sender_id,
                    },
                )
            except Exception:
                # do not fail the API if FCM fails
                pass

        return {"status": "ok", "message_id": message_id, "receiver_id": receiver_id}

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.get("", response_model=MessagesListOut)
def get_messages(relationship_id: int, after_id: int = 0, limit: int = 200):
    try:
        with get_db.begin() as conn:
            rows = crud.list_messages(conn, relationship_id, after_id, limit)

        return MessagesListOut(
            relationship_id=relationship_id,
            messages=[
                MessageOut(
                    message_id=r["MessageID"],
                    relationship_id=r["RelationshipID"],
                    sender_id=r["SenderID"],
                    message_text=r["message_text"],
                    is_read=bool(r["IsRead"]),
                    sent_at=r["SentAt"],
                )
                for r in rows
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@router.put("/read", response_model=dict)
def mark_read(payload: MarkReadIn):
    try:
        with get_db.begin() as conn:
            # validate reader belongs to relationship
            _ = crud.validate_sender_and_get_receiver(conn, payload.relationship_id, payload.reader_id)
            updated = crud.mark_messages_read(conn, payload.relationship_id, payload.message_ids)

        return {"status": "ok", "updated": updated}

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")