from pathlib import Path
import firebase_admin
from firebase_admin import credentials, messaging

BASE_DIR = Path(__file__).resolve().parent.parent
SERVICE_ACCOUNT_PATH = BASE_DIR / "services" / "serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))
    firebase_admin.initialize_app(cred)


def send_medication_push(token: str, title: str, body: str, data: dict | None = None):
    """
    High priority Android push.
    Channel id 'med_reminders' must exist in the elder app.
    """
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in (data or {}).items()},
        android=messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(
                channel_id="med_reminders",
                sound="default",
                default_vibrate_timings=True,
            ),
        ),
        token=token,
    )
    return messaging.send(message)


# ✅ Backward-compatible name (so your notifications router keeps working)
def send_push_notification(token: str, title: str, body: str, data: dict | None = None):
    return send_medication_push(token=token, title=title, body=body, data=data)