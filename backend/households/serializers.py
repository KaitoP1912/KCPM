from rest_framework import serializers

from households.models import Household, HouseholdMember


class HouseholdSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(
        source='owner.email',
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
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'owner',
        ]


class HouseholdMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    class Meta:
        model = HouseholdMember
        fields = [
            'id',
            'household',
            'user',
            'user_email',
            'role',
            'joined_at',
        ]