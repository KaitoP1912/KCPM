import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from notifications.models import FCMDevice


SAVE_FCM_TOKEN_URL = "/api/notifications/save-fcm-token/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_save_fcm_token_success():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        SAVE_FCM_TOKEN_URL,
        {
            "token": "fcm_token_12345",
            "device_type": "android",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    fcm_device = FCMDevice.objects.filter(
        token="fcm_token_12345"
    ).first()
    assert fcm_device is not None
    assert fcm_device.user == user
    assert fcm_device.is_active is True


@pytest.mark.django_db
def test_save_fcm_token_with_ios_device():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        SAVE_FCM_TOKEN_URL,
        {
            "token": "ios_fcm_token_12345",
            "device_type": "ios",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    fcm_device = FCMDevice.objects.filter(
        token="ios_fcm_token_12345"
    ).first()
    assert fcm_device is not None
    assert fcm_device.device_type == "ios"


@pytest.mark.django_db
def test_save_fcm_token_default_device_type():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        SAVE_FCM_TOKEN_URL,
        {
            "token": "fcm_token_no_type",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    fcm_device = FCMDevice.objects.filter(
        token="fcm_token_no_type"
    ).first()
    assert fcm_device is not None
    assert fcm_device.device_type in ["android", FCMDevice.DeviceType.ANDROID]


@pytest.mark.django_db
def test_save_fcm_token_missing_token():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        SAVE_FCM_TOKEN_URL,
        {
            "device_type": "android",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_save_fcm_token_unauthenticated():
    client = APIClient()

    response = client.post(
        SAVE_FCM_TOKEN_URL,
        {
            "token": "fcm_token_12345",
            "device_type": "android",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_save_fcm_token_update_existing():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    FCMDevice.objects.create(
        user=user,
        token="existing_token",
        device_type="android",
        is_active=False,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        SAVE_FCM_TOKEN_URL,
        {
            "token": "existing_token",
            "device_type": "ios",
        },
        format="json",
    )

    assert response.status_code == 200

    fcm_device = FCMDevice.objects.filter(
        token="existing_token"
    ).first()
    assert fcm_device is not None
    assert fcm_device.device_type == "ios"
    assert fcm_device.is_active is True
