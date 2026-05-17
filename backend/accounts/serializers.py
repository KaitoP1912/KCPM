from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'full_name',
            'phone_number',
            'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'full_name',
            'phone_number',
            'avatar',
            'avatar_url',
            'bank_name',
            'bank_account_number',
            'bank_account_holder',
        ]

        read_only_fields = [
            'id',
            'email',
            'username',
            'avatar_url',
        ]

    def get_avatar_url(self, obj):
        request = self.context.get('request')

        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)

        return ''

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):
        if (
            attrs['new_password']
            != attrs['confirm_password']
        ):
            raise serializers.ValidationError(
                {
                    'confirm_password':
                    'Mật khẩu xác nhận không khớp'
                }
            )

        return attrs