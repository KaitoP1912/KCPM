import firebase_admin

from django.conf import settings
from firebase_admin import credentials, messaging

from notifications.models import FCMDevice


def initialize_firebase():
    if firebase_admin._apps:
        return

    service_account_path = settings.BASE_DIR / 'firebase-service-account.json'

    cred = credentials.Certificate(service_account_path)

    firebase_admin.initialize_app(cred)


def send_push_notification_to_user(
    user,
    title,
    body,
    data=None,
):
    initialize_firebase()

    devices = FCMDevice.objects.filter(
        user=user,
        is_active=True
    )

    for device in devices:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={
                    key: str(value)
                    for key, value in (data or {}).items()
                },
                token=device.token,
            )

            messaging.send(message)

        except Exception as e:
            print('FCM ERROR:', e)
            device.is_active = False
            device.save(update_fields=['is_active'])