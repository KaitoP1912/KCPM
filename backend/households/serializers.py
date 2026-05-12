from rest_framework import serializers
from django.contrib.auth import get_user_model
from households.models import Household, HouseholdMember

User = get_user_model()

class HouseholdMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)

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
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    members = HouseholdMemberSerializer(many=True, read_only=True)

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