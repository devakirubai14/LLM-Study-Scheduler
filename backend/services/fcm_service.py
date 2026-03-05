import os
import firebase_admin
from firebase_admin import credentials, messaging

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
cred_path = os.path.join(BASE_DIR, "firebase_key.json")

cred = credentials.Certificate(cred_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)


def send_push_notification(device_token, title, body):

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=device_token
    )

    response = messaging.send(message)

    return response