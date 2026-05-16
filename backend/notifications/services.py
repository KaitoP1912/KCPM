from notifications.firebase_service import send_push_notification_to_user
from notifications.models import Notification


def create_notification(
    *,
    recipient,
    actor,
    notification_type,
    title,
    household=None,
    amount=None,
    level=Notification.Level.PUSH,
    metadata=None,
    push_title='Chung Ví',
    push_body=None,
):
    notification = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        household=household,
        notification_type=notification_type,
        level=level,
        title=title,
        amount=amount,
        metadata=metadata or {},
    )

    try:
        send_push_notification_to_user(
            user=recipient,
            title=push_title,
            body=push_body or title,
            data={
                'notification_id': str(notification.id),
                'notification_type': notification.notification_type,
                'household_id': (
                    str(household.id)
                    if household else ''
                ),
            },
        )

        print(
            f'FCM SUCCESS: {recipient.email} - {title}'
        )

    except Exception as e:
        print('FCM SEND ERROR:', e)

    return notification