# app/services/fcm_service.py

import firebase_admin
from firebase_admin import credentials, messaging
from pathlib import Path

# Get absolute path to this file
BASE_DIR = Path(__file__).resolve().parent.parent

# If your file is inside: app/firebase/serviceAccountKey.json
SERVICE_ACCOUNT_PATH = BASE_DIR / "services" / "serviceAccountKey.json"

if not firebase_admin._apps:
    if not SERVICE_ACCOUNT_PATH.exists():
        raise FileNotFoundError(f"Firebase key not found at {SERVICE_ACCOUNT_PATH}")

    cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))
    firebase_admin.initialize_app(cred)


def send_push_notification(token: str, title: str, body: str, data: dict | None = None):

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        token=token,
    )

    return messaging.send(message)