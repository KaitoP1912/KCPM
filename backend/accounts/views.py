from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from notifications.models import FCMDevice

from accounts.serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordRequestSerializer,
    ResetPasswordSerializer,
    VerifyRegisterOTPSerializer,
    ResendRegisterOTPSerializer,
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

from rest_framework_simplejwt.views import (
    TokenObtainPairView
)

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer
)

import requests as pyrequests

User = get_user_model()

OTP_EXPIRE_SECONDS = 600
OTP_RESEND_COOLDOWN = 60


def generate_otp():
    return str(
        random.randint(100000, 999999)
    )


def send_register_otp(email, otp):
    send_mail(
        subject='Xác thực email Chung Ví',
        message=(
            f'Mã OTP xác thực tài khoản của bạn là: {otp}\n\n'
            'OTP có hiệu lực trong 10 phút.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        otp = generate_otp()

        cache.set(
            f'register_otp:{user.email}',
            otp,
            timeout=OTP_EXPIRE_SECONDS,
        )

        cache.set(
            f'register_otp_cooldown:{user.email}',
            True,
            timeout=OTP_RESEND_COOLDOWN,
        )

        send_register_otp(
            user.email,
            otp,
        )

        return Response(
            {
                'message': (
                    'Đăng ký thành công. '
                    'Vui lòng xác thực email.'
                ),
                'email': user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyRegisterOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyRegisterOTPSerializer(
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

        user = User.objects.filter(
            email=email
        ).first()

        if not user:
            return Response(
                {
                    'detail':
                    'Người dùng không tồn tại'
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        cached_otp = cache.get(
            f'register_otp:{email}'
        )

        if not cached_otp:
            return Response(
                {
                    'detail':
                    'OTP đã hết hạn'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if cached_otp != otp:
            return Response(
                {
                    'detail':
                    'OTP không chính xác'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.email_verified = True
        user.is_active = True

        user.save()

        cache.delete(
            f'register_otp:{email}'
        )

        return Response(
            {
                'message':
                'Xác thực email thành công'
            },
            status=status.HTTP_200_OK,
        )


class ResendRegisterOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = (
            ResendRegisterOTPSerializer(
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
                    'Nếu email tồn tại OTP sẽ được gửi.'
                },
                status=status.HTTP_200_OK,
            )

        if user.email_verified:
            return Response(
                {
                    'detail':
                    'Email đã xác thực'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        cooldown = cache.get(
            f'register_otp_cooldown:{email}'
        )

        if cooldown:
            return Response(
                {
                    'detail': (
                        'Vui lòng đợi 60 giây '
                        'để gửi lại OTP.'
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp = generate_otp()

        cache.set(
            f'register_otp:{email}',
            otp,
            timeout=OTP_EXPIRE_SECONDS,
        )

        cache.set(
            f'register_otp_cooldown:{email}',
            True,
            timeout=OTP_RESEND_COOLDOWN,
        )

        send_register_otp(
            email,
            otp,
        )

        return Response(
            {
                'message':
                'OTP đã được gửi lại.'
            },
            status=status.HTTP_200_OK,
        )


class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.email_verified:
            raise ValidationError(
                {
                    'detail':
                    'Email chưa được xác thực'
                }
            )

        return data


class CustomTokenObtainPairView(
    TokenObtainPairView
):
    serializer_class = (
        CustomTokenObtainPairSerializer
    )


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
                    'is_active': True,
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