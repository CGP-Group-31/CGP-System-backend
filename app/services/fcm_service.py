from pathlib import Path
import firebase_admin
from firebase_admin import credentials, messaging

BASE_DIR = Path(__file__).resolve().parent.parent
SERVICE_ACCOUNT_PATH = BASE_DIR / "services" / "serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))
    firebase_admin.initialize_app(cred)


def send_medication_push(token: str, title: str, body: str, data: dict | None = None):

    if not token:
        return None
    # payload = {k: str(v) for k, v in (data or {}).items()}
    payload = {}

    if data:
        for key, value in data.items():
            payload[key] = str(value)

        # Take the dictionary.
        # If it exists, convert all values to text.
        # If it doesn't exist, use empty dictionary.

    payload["title"] = title
    payload["body"] = body

    message = messaging.Message(
        data=payload,  #  data-only for reliable app handling
        android=messaging.AndroidConfig(
            priority="high",
        ),
        token=token,
    )
    return messaging.send(message)


def send_push_notification(token: str, title: str, body: str, data: dict | None = None):
    return send_medication_push(token=token, title=title, body=body, data=data)