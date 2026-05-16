from django.contrib import admin

from notifications.models import FCMDevice, Notification


@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'device_type',
        'is_active',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'user__email',
        'token',
    ]
    list_filter = [
        'device_type',
        'is_active',
    ]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'recipient',
        'actor',
        'notification_type',
        'level',
        'is_read',
        'created_at',
    ]
    search_fields = [
        'recipient__email',
        'actor__email',
        'title',
    ]
    list_filter = [
        'notification_type',
        'level',
        'is_read',
    ]