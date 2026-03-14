# app/services/appointment_scheduler.py

from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.fcm_service import send_push_notification

TZ = ZoneInfo("Asia/Colombo")


def _get_latest_token(db: Session, user_id: int, app_type: str) -> str | None:
    q = text("""SELECT TOP 1 FCMToken FROM UserDevices
        WHERE UserID = :uid
          AND app_type = :app_type
          AND FCMToken IS NOT NULL
          AND LTRIM(RTRIM(FCMToken)) <> '' ORDER BY LastUpdated DESC;""")
    row = db.execute(q, {"uid": user_id, "app_type": app_type}).fetchone()
    return row.FCMToken if row else None


def _get_primary_caregiver_id(db: Session, elder_id: int) -> int | None:
    q = text("""SELECT TOP 1 CaregiverID FROM CareRelationships WHERE ElderID = :eid AND IsPrimary = 1
        ORDER BY IsPrimary DESC, RelationshipID ASC;""")
    row = db.execute(q, {"eid": elder_id}).fetchone()
    return int(row.CaregiverID) if row else None


def run_due_appointment_reminders(db: Session):
  

  
    now = datetime.now(TZ)

    q = text("""SELECT ar.ReminderID, ar.ReminderType, ar.AppointmentID, ar.ScheduledFor,
             a.ElderID, a.DoctorName, a.Title, a.Location,
            a.Notes,
            a.AppointmentDate,
            a.AppointmentTime,
            u.FullName
        FROM AppointmentReminders ar
        JOIN Appointments a ON a.AppointmentID = ar.AppointmentID
        JOIN Users u ON u.UserID = a.ElderID
        WHERE ar.Status = 'PENDING'
          AND ar.ScheduledFor <= :now
        ORDER BY ar.ScheduledFor ASC;""")

    rows = db.execute(q, {"now": now}).fetchall()

    for r in rows:
        elder_id = int(r.ElderID)

        caregiver_id = _get_primary_caregiver_id(db, elder_id)
        elder_token = _get_latest_token(db, elder_id, "elder")
        caregiver_token = _get_latest_token(db, caregiver_id, "caregiver") if caregiver_id else None

        elder_name = (str(r.FullName) if r.FullName else "").strip() or "there"

        # appointment time
        appt_time_str = str(r.AppointmentTime)[:5]  # HH:MM
        appt_dt_text = f"{r.AppointmentDate} {appt_time_str}"

        label = "tomorrow" if str(r.ReminderType).upper() in ("24H", "APPT_24H") else "in 6 hours"

        elder_title = "Doctor Appointment Reminder"
        elder_body = (
            f"Hi {elder_name}, you have a doctor appointment {label}.\n\n"
            f"Title: {r.Title or 'Appointment'}\n"
            f"Doctor: {r.DoctorName or '-'}\n"
            f"Time: {appt_dt_text}\n"
            f"Place: {r.Location or '-'}\n"
        )

        caregiver_title = "Appointment Reminder"
        caregiver_body = (
            f"Reminder: {elder_name} has an appointment {label}.\n\n"
            f"Title: {r.Title or 'Appointment'}\n"
            f"Doctor: {r.DoctorName or '-'}\n"
            f"Time: {appt_dt_text}\n"
            f"Place: {r.Location or '-'}\n"
        )

        data_payload = {
            "type": "APPT_REMINDER",
            "appointmentId": str(r.AppointmentID),
            "elderId": str(elder_id),
            "reminderType": str(r.ReminderType),
            "appointmentDate": str(r.AppointmentDate),
            "appointmentTime": str(r.AppointmentTime)[:5],
            "title": r.Title or "",
            "doctorName": r.DoctorName or "",
            "location": r.Location or "",
            "notes": r.Notes or "",
        }

        sent_any = False

        if elder_token:
            try:
                send_push_notification(elder_token, elder_title, elder_body, data_payload)
                sent_any = True
            except Exception:
                pass

        if caregiver_token:
            try:
                send_push_notification(caregiver_token, caregiver_title, caregiver_body, data_payload)
                sent_any = True
            except Exception:
                pass

        upd = text("""UPDATE AppointmentReminders SET Status = :status,
                SentAt = CASE WHEN :status='SENT' THEN GETDATE() ELSE SentAt END
            WHERE ReminderID = :rid;""")
        db.execute(upd, {"status": "SENT" if sent_any else "SKIPPED", "rid": r.ReminderID})

    db.commit()