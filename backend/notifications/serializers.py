from rest_framework import serializers

from notifications.models import FCMDevice, Notification


class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = [
            'id',
            'token',
            'device_type',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'is_active',
            'created_at',
            'updated_at',
        ]


class NotificationSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()
    household_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'level',
            'title',
            'amount',
            'is_read',
            'metadata',
            'actor_name',
            'household_name',
            'created_at',
            'updated_at',
        ]

    def get_actor_name(self, obj):
        return obj.actor.full_name or obj.actor.email

    def get_household_name(self, obj):
        if obj.household:
            return obj.household.name
        return None