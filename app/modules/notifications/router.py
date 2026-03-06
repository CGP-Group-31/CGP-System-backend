# app/modules/notifications/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.services.fcm_service import send_push_notification
from app.services.appointment_scheduler import run_due_appointment_reminders

from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
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

TZ = ZoneInfo("Asia/Colombo")


class DevApptTestRequest(BaseModel):
    elderId: int
    title: str = "Doctor Appointment"
    doctorName: str = "Dr. Test"
    location: str = "Test Hospital"
    notes: str = "This is a DEV test reminder"
    appointmentDate: str | None = None   # "YYYY-MM-DD"
    appointmentTime: str | None = None   # "HH:MM"
    reminderType: str = "24H"            # "24H" or "6H"


def _get_latest_token(db: Session, user_id: int, app_type: str) -> str | None:
    q = text("""SELECT TOP 1 FCMToken FROM UserDevices WHERE UserID = :uid
          AND app_type = :app_type
          AND FCMToken IS NOT NULL
          AND LTRIM(RTRIM(FCMToken)) <> ''
        ORDER BY LastUpdated DESC;""")
    row = db.execute(q, {"uid": user_id, "app_type": app_type}).fetchone()
    return row.FCMToken if row else None


def _get_primary_caregiver_id(db: Session, elder_id: int) -> int | None:
    q = text("""SELECT TOP 1 CaregiverID FROM CareRelationships
        WHERE ElderID = :eid ORDER BY IsPrimary DESC, RelationshipID ASC;""")
    row = db.execute(q, {"eid": elder_id}).fetchone()
    return int(row.CaregiverID) if row else None


@router.post("/dev/test-appointment")
def dev_test_appointment_push(req: DevApptTestRequest, db: Session = Depends(get_db)):
    u = db.execute(
        text("SELECT FullName FROM Users WHERE UserID = :eid"),
        {"eid": req.elderId},
    ).fetchone()

    elder_name = (str(u.FullName) if u and u.FullName else "").strip() or "there"

    
    elder_token = _get_latest_token(db, req.elderId, "elder")
    caregiver_id = _get_primary_caregiver_id(db, req.elderId)
    caregiver_token = _get_latest_token(db, caregiver_id, "caregiver") if caregiver_id else None

    if not elder_token and not caregiver_token:
        raise HTTPException(
            status_code=404,
            detail="No device tokens found for elder/caregiver. Check UserDevices table.",
        )

    now = datetime.now(TZ)
    appt_date = req.appointmentDate or now.date().isoformat()
    appt_time = req.appointmentTime or now.strftime("%H:%M")

    label = "tomorrow" if req.reminderType.upper() in ("24H", "APPT_24H") else "in 6 hours"
    appt_dt_text = f"{appt_date} {appt_time}"

    elder_title = "Doctor Appointment Reminder"
    elder_body = (
        f"Hi {elder_name}, you have a doctor appointment {label}.\n\n"
        f"Title: {req.title}\n"
        f"Doctor: {req.doctorName}\n"
        f"Time: {appt_dt_text}\n"
        f"Place: {req.location}\n"
    )

    caregiver_title = "Appointment Reminder"
    caregiver_body = (
        f"Reminder: {elder_name} has an appointment {label}.\n\n"
        f"Title: {req.title}\n"
        f"Doctor: {req.doctorName}\n"
        f"Time: {appt_dt_text}\n"
        f"Place: {req.location}\n"
    )

    data_payload = {
        "type": "APPT_REMINDER",
        "appointmentId": "DEV", 
        "elderId": str(req.elderId),
        "reminderType": req.reminderType,
        "appointmentDate": appt_date,
        "appointmentTime": appt_time,
        "title": req.title,
        "doctorName": req.doctorName,
        "location": req.location,
        "notes": req.notes,
    }

    sent = {"elder": False, "caregiver": False}

    if elder_token:
        try:
            send_push_notification(elder_token, elder_title, elder_body, data_payload)
            sent["elder"] = True
        except Exception as e:
            sent["elder_error"] = str(e)

    if caregiver_token:
        try:
            send_push_notification(caregiver_token, caregiver_title, caregiver_body, data_payload)
            sent["caregiver"] = True
        except Exception as e:
            sent["caregiver_error"] = str(e)

    return {
        "ok": sent["elder"] or sent["caregiver"],
        "sent": sent,
        "elderId": req.elderId,
        "caregiverId": caregiver_id,
    }