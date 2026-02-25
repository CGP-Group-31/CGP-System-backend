# app/modules/notifications/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.services.fcm_service import send_push_notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/test/{user_id}")
def test_notification(user_id: int, db: Session = Depends(get_db)):
   
    q1 = text("SELECT FCMToken FROM UserDevices WHERE UserID = :uid")
    row = db.execute(q1, {"uid": user_id}).fetchone()

    token = row[0] if row and row[0] else None


    if not token:
        raise HTTPException(status_code=404, detail="FCM token not found for this user")

    # Send FCM push
    msg_id = send_push_notification(
        token=token,
        title="FCM Test",
        body="HI, This is a test notification",
        data={"type": "test"}
    )

    return {"message": "sent", "firebase_message_id": msg_id}