from pathlib import Path
import firebase_admin
from firebase_admin import credentials, messaging
from app.core.config import settings


BASE_DIR = Path(__file__).resolve().parent.parent

SERVICE_ACCOUNT_PATH = Path(settings.FIREBASE_CREDENTIALS_PATH)

if not SERVICE_ACCOUNT_PATH.is_absolute():
    SERVICE_ACCOUNT_PATH = BASE_DIR / settings.FIREBASE_CREDENTIALS_PATH


if not firebase_admin._apps:
    cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))
    firebase_admin.initialize_app(cred)


def send_medication_push(token: str, title: str, body: str, data: dict | None = None):
    if not token:
        return None

    payload = {}

    # Convert all values to string (FCM requires string values)
    if data:
        for key, value in data.items():
            payload[key] = str(value)

    # Add title/body into data (data-only message)
    payload["title"] = title
    payload["body"] = body

    message = messaging.Message(
        data=payload,
        android=messaging.AndroidConfig(
            priority="high",
        ),
        token=token,
    )
    return messaging.send(message)


def send_push_notification(token: str, title: str, body: str, data: dict | None = None):
    return send_medication_push(token=token, title=title, body=body, data=data)