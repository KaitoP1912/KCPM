from django.contrib.auth import get_user_model
from rest_framework import serializers

from households.models import (
    Activity,
    Household,
    HouseholdMember,
)

User = get_user_model()


class HouseholdMemberSerializer(serializers.ModelSerializer):
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


class HouseholdSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(
        source='owner.email',
        read_only=True
    )
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
            'owner',
            'owner_email',
            'members',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['owner']


class AddHouseholdMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=HouseholdMember.Role.choices,
        default=HouseholdMember.Role.MEMBER
    )

    def validate_email(self, value):
        try:
            self.user_to_add = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Không tìm thấy người dùng với email này.'
            )
        return value


class ActivitySerializer(serializers.ModelSerializer):
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
        return obj.actor.full_name or obj.actor.email