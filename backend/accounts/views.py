from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import FCMDevice
from accounts.serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

from django.contrib.auth.hashers import check_password


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class SaveFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')

        if not token:
            return Response(
                {'detail': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        FCMDevice.objects.update_or_create(
            token=token,
            defaults={
                'user': request.user,
                'device_type': request.data.get(
                    'device_type',
                    'android'
                ),
            }
        )

        return Response(
            {'message': 'FCM token saved successfully'},
            status=status.HTTP_200_OK
        )
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = request.user

        old_password = serializer.validated_data[
            'old_password'
        ]

        new_password = serializer.validated_data[
            'new_password'
        ]

        if not check_password(
            old_password,
            user.password
        ):
            return Response(
                {
                    'detail':
                    'Mật khẩu hiện tại không đúng'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)

        user.save()

        return Response(
            {
                'message':
                'Đổi mật khẩu thành công'
            },
            status=status.HTTP_200_OK
        )