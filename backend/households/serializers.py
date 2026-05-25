from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db.models import Sum

from households.models import (
    Activity,
    Household,
    HouseholdMember,
)

User = get_user_model()

VIRTUAL_MEMBER_EMAIL_DOMAIN = '@virtual.chungvi.local'


def is_virtual_user(user):
    email = (getattr(user, 'email', '') or '').lower()
    return email.endswith(VIRTUAL_MEMBER_EMAIL_DOMAIN)


def get_user_display_name(user):
    if is_virtual_user(user):
        return user.full_name or 'Thành viên ảo'

    return user.full_name or user.email


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

    user_avatar = serializers.SerializerMethodField()

    is_virtual = serializers.SerializerMethodField()

    class Meta:
        model = HouseholdMember

        fields = [
            'id',
            'user',
            'user_email',
            'user_full_name',
            'user_avatar',
            'role',
            'is_virtual',
            'joined_at',
        ]

    def get_user_avatar(self, obj):
        request = self.context.get('request')

        if obj.user.avatar and request:
            return request.build_absolute_uri(
                obj.user.avatar.url
            )

        return ''

    def get_is_virtual(self, obj):
        return is_virtual_user(obj.user)


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


class CreateVirtualMemberSerializer(serializers.Serializer):
    display_name = serializers.CharField(
        max_length=80
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255
    )

    def validate_display_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError(
                'Tên thành viên ảo quá ngắn.'
            )

        return value


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
        return get_user_display_name(obj.actor)


class HouseholdSummarySerializer(
    serializers.ModelSerializer
):
    avatar_url = serializers.SerializerMethodField()

    member_count = serializers.SerializerMethodField()

    expense_count = serializers.SerializerMethodField()

    total_owe = serializers.SerializerMethodField()

    total_receive = serializers.SerializerMethodField()

    latest_activity = serializers.SerializerMethodField()

    class Meta:
        model = Household

        fields = [
            'id',
            'name',
            'avatar_url',

            'member_count',
            'expense_count',

            'total_owe',
            'total_receive',

            'latest_activity',

            'updated_at',
        ]

    def get_avatar_url(self, obj):
        request = self.context.get('request')

        if obj.avatar and request:
            return request.build_absolute_uri(
                obj.avatar.url
            )

        return ''

    def get_member_count(self, obj):
        return obj.members.count()

    def get_expense_count(self, obj):
        return obj.expenses.count()

    def get_total_owe(self, obj):
        request = self.context.get('request')

        if not request:
            return 0

        total = obj.debts.filter(
            from_user=request.user,
            is_paid=False,
        ).aggregate(
            total=Sum('amount')
        )['total']

        return total or 0

    def get_total_receive(self, obj):
        request = self.context.get('request')

        if not request:
            return 0

        total = obj.debts.filter(
            to_user=request.user,
            is_paid=False,
        ).aggregate(
            total=Sum('amount')
        )['total']

        return total or 0

    def get_latest_activity(self, obj):
        latest = obj.activities.order_by(
            '-created_at'
        ).first()

        if not latest:
            return ''

        return latest.title
