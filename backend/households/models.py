from django.conf import settings
from django.db import models

from core.models import BaseModel


class Household(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='households/',
        blank=True,
        null=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_households'
    )

    def __str__(self):
        return self.name


class HouseholdMember(BaseModel):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Chủ nhóm'
        ADMIN = 'admin', 'Quản trị viên'
        MEMBER = 'member', 'Thành viên'

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='household_memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('household', 'user')

    def __str__(self):
        return f'{self.user.email} - {self.household.name}'


class Activity(BaseModel):
    class ActivityType(models.TextChoices):
        GROUP_CREATED = 'group_created', 'Tạo nhóm'
        EXPENSE_CREATED = 'expense_created', 'Thêm khoản chi'
        EXPENSE_UPDATED = 'expense_updated', 'Sửa khoản chi'
        EXPENSE_DELETED = 'expense_deleted', 'Xóa khoản chi'
        MEMBER_JOINED = 'member_joined', 'Thêm thành viên'
        PAYMENT_CREATED = 'payment_created', 'Thanh toán'

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=50,
        choices=ActivityType.choices
    )
    title = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True
    )
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class Notification(BaseModel):
    class NotificationType(models.TextChoices):
        ADDED_TO_GROUP = 'added_to_group', 'Được thêm vào nhóm'
        MEMBER_ADDED_TO_GROUP = 'member_added_to_group', 'Thành viên mới'
        DEBT_CREATED = 'debt_created', 'Phát sinh công nợ'
        EXPENSE_UPDATED = 'expense_updated', 'Khoản chi được cập nhật'
        EXPENSE_DELETED = 'expense_deleted', 'Khoản chi bị xóa'
        DEBT_REMINDER_RECEIVED = 'debt_reminder_received', 'Nhận nhắc nợ'
        DEBT_REMINDER_SENT = 'debt_reminder_sent', 'Đã nhắc nợ'
        PAYMENT_RECEIVED = 'payment_received', 'Nhận thanh toán'
        PAYMENT_SENT = 'payment_sent', 'Đã thanh toán'
        PAYMENT_CONFIRMED = 'payment_confirmed', 'Xác nhận thanh toán'

    class Level(models.TextChoices):
        PUSH = 'push', 'Push notification'
        IN_APP = 'in_app', 'Thông báo trong app'

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
        Household,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=60,
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