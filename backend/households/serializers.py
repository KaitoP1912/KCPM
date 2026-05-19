from django.contrib.auth import get_user_model
from rest_framework import serializers

from households.models import (
    Activity,
    Household,
    HouseholdMember,
)

User = get_user_model()


class HouseholdMemberSerializer(
    serializers.ModelSerializer
):
    user_email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    user_full_name = serializers.CharField(
        source='user.full_name',
        read_only=True
    )

    class Meta:
        model = HouseholdMember

        fields = [
            'id',
            'user',
            'user_email',
            'user_full_name',
            'role',
            'joined_at',
        ]


class HouseholdSerializer(
    serializers.ModelSerializer
):
    owner_email = serializers.EmailField(
        source='owner.email',
        read_only=True
    )

    avatar_url = serializers.SerializerMethodField()

    members = HouseholdMemberSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Household

        fields = [
            'id',
            'name',
            'description',
            'avatar',
            'avatar_url',
            'owner',
            'owner_email',
            'invite_code',
            'is_active',
            'members',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'owner',
            'invite_code',
            'is_active',
        ]

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                'Tên nhóm quá ngắn.'
            )

        return value

    def get_avatar_url(self, obj):
        request = self.context.get('request')

        if obj.avatar and request:
            return request.build_absolute_uri(
                obj.avatar.url
            )

        return ''


class JoinHouseholdSerializer(
    serializers.Serializer
):
    invite_code = serializers.CharField()

    def validate_invite_code(self, value):
        return value.strip().upper()


class ActivitySerializer(
    serializers.ModelSerializer
):
    actor_name = serializers.SerializerMethodField()

    household_name = serializers.CharField(
        source='household.name',
        read_only=True
    )

    class Meta:
        model = Activity

        fields = [
            'id',
            'household',
            'household_name',
            'activity_type',
            'title',
            'amount',
            'metadata',
            'actor_name',
            'created_at',
        ]

    def get_actor_name(self, obj):
        return (
            obj.actor.full_name
            or obj.actor.email
        )