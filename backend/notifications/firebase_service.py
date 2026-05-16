import firebase_admin

from django.conf import settings
from firebase_admin import credentials
from firebase_admin import messaging

from notifications.models import FCMDevice


def initialize_firebase():
    if firebase_admin._apps:
        return

    service_account_path = (
        settings.BASE_DIR /
        'firebase-service-account.json'
    )

    cred = credentials.Certificate(
        service_account_path
    )

    firebase_admin.initialize_app(cred)

    print('FIREBASE INITIALIZED')


def send_push_notification_to_user(
    user,
    title,
    body,
    data=None,
):
    initialize_firebase()

    devices = FCMDevice.objects.filter(
        user=user,
        is_active=True,
    )

    print(
        f'SENDING PUSH TO {user.email}: '
        f'{devices.count()} devices'
    )

    for device in devices:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),

                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='chung_vi_channel',
                    ),
                ),

                data={
                    key: str(value)
                    for key, value
                    in (data or {}).items()
                },

                token=device.token,
            )

            response = messaging.send(message)

            print(
                f'FCM SUCCESS: '
                f'{device.user.email} - {response}'
            )

        except Exception as e:
            print('FCM ERROR:', e)

            device.is_active = False

            device.save(
                update_fields=['is_active']
            )