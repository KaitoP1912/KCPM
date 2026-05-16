import firebase_admin

from firebase_admin import credentials
from firebase_admin import messaging

from django.conf import settings

from notifications.models import FCMDevice

if not firebase_admin._apps:
    cred = credentials.Certificate(
        settings.BASE_DIR / 'firebase-service-account.json'
    )

    firebase_admin.initialize_app(cred)


def send_push_notification(
    user,
    title,
    body,
    data=None,
):
    devices = FCMDevice.objects.filter(user=user)

    for device in devices:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=device.token,
            )

            messaging.send(message)

        except Exception as e:
            print('FCM ERROR:', e)