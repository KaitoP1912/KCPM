from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import FCMDevice
from accounts.serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


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