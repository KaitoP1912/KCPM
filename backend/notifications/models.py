from django.conf import settings
from django.db import models

from core.models import BaseModel


class FCMDevice(BaseModel):
    class DeviceType(models.TextChoices):
        ANDROID = 'android', 'Android'
        IOS = 'ios', 'iOS'
        WEB = 'web', 'Web'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fcm_devices'
    )

    token = models.TextField(unique=True)

    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.ANDROID
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.email} - {self.device_type}'


class Notification(BaseModel):
    class NotificationType(models.TextChoices):
        ADDED_TO_GROUP = 'added_to_group', 'Được thêm vào nhóm'
        MEMBER_ADDED_TO_GROUP = 'member_added_to_group', 'Thành viên mới'
        DEBT_CREATED = 'debt_created', 'Phát sinh công nợ'
        DEBT_REMINDER_RECEIVED = 'debt_reminder_received', 'Nhận nhắc nợ'
        DEBT_REMINDER_SENT = 'debt_reminder_sent', 'Đã nhắc nợ'
        PAYMENT_RECEIVED = 'payment_received', 'Nhận thanh toán'
        PAYMENT_SENT = 'payment_sent', 'Đã thanh toán'

    class Level(models.TextChoices):
        IN_APP = 'in_app', 'Trong app'
        PUSH = 'push', 'Push notification'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='triggered_notifications'
    )

    household = models.ForeignKey(
        'households.Household',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )

    notification_type = models.CharField(
        max_length=80,
        choices=NotificationType.choices
    )

    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.IN_APP
    )

    title = models.CharField(max_length=255)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True
    )

    is_read = models.BooleanField(default=False)

    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title