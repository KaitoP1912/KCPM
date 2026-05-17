from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import FCMDevice
from accounts.serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordRequestSerializer,
    ResetPasswordSerializer,
)

from django.contrib.auth.hashers import check_password
import random
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import RefreshToken
import requests as pyrequests

User = get_user_model()

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
    
class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = (
            ForgotPasswordRequestSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data[
            'email'
        ].lower()

        user = User.objects.filter(
            email=email
        ).first()

        if not user:
            return Response(
                {
                    'message':
                    'Nếu email tồn tại, OTP sẽ được gửi.'
                },
                status=status.HTTP_200_OK
            )

        otp = str(
            random.randint(100000, 999999)
        )

        cache.set(
            f'forgot_password_otp:{email}',
            otp,
            timeout=600
        )

        send_mail(
            subject='Mã OTP đặt lại mật khẩu Chung Ví',
            message=(
                f'Mã OTP của bạn là: {otp}\n\n'
                'OTP có hiệu lực trong 10 phút.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {
                'message':
                'OTP đã được gửi tới email.'
            },
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data[
            'email'
        ].lower()

        otp = serializer.validated_data[
            'otp'
        ]

        new_password = serializer.validated_data[
            'new_password'
        ]

        cached_otp = cache.get(
            f'forgot_password_otp:{email}'
        )

        if not cached_otp:
            return Response(
                {
                    'detail':
                    'OTP đã hết hạn'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if cached_otp != otp:
            return Response(
                {
                    'detail':
                    'OTP không chính xác'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(
            email=email
        ).first()

        if not user:
            return Response(
                {
                    'detail':
                    'Người dùng không tồn tại'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        user.set_password(new_password)

        user.save()

        cache.delete(
            f'forgot_password_otp:{email}'
        )

        return Response(
            {
                'message':
                'Đặt lại mật khẩu thành công'
            },
            status=status.HTTP_200_OK
        )
    
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')

        if not token:
            return Response(
                {
                    'detail': 'Thiếu token Google'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            try:
                idinfo = id_token.verify_oauth2_token(
                    token,
                    requests.Request(),
                )

            except Exception:
                userinfo_response = pyrequests.get(
                    'https://www.googleapis.com/oauth2/v1/userinfo',
                    params={
                        'access_token': token
                    }
                )

                idinfo = userinfo_response.json()

            email = idinfo.get('email')

            if not email:
                return Response(
                    {
                        'detail': 'Không lấy được email'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            full_name = idinfo.get(
                'name',
                ''
            )

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'full_name': full_name,
                    'auth_provider': 'google',
                    'email_verified': True,
                }
            )

            if created:
                user.set_unusable_password()
                user.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'access': str(
                        refresh.access_token
                    ),

                    'refresh': str(refresh),

                    'user': {
                        'email': user.email,
                        'full_name':
                        user.full_name,
                    }
                }
            )

        except Exception as e:
            print(e)

            return Response(
                {
                    'detail':
                    'Google token không hợp lệ'
                },
                status=status.HTTP_400_BAD_REQUEST
            )