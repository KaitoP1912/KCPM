import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient


RESEND_REGISTER_OTP_URL = "/api/auth/resend-register-otp/"


@pytest.mark.django_db
def test_resend_register_otp_success():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="testuser@example.com",
        username="testuser",
        password="StrongPass123",
        email_verified=False,
        is_active=False,
    )

    response = client.post(
        RESEND_REGISTER_OTP_URL,
        {
            "email": "testuser@example.com",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data


@pytest.mark.django_db
def test_resend_register_otp_missing_email():
    client = APIClient()

    response = client.post(
        RESEND_REGISTER_OTP_URL,
        {},
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "email" in data


@pytest.mark.django_db
def test_resend_register_otp_already_verified():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="testuser@example.com",
        username="testuser",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    response = client.post(
        RESEND_REGISTER_OTP_URL,
        {
            "email": "testuser@example.com",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "xác thực" in data["detail"]


@pytest.mark.django_db
def test_resend_register_otp_cooldown():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="testuser@example.com",
        username="testuser",
        password="StrongPass123",
        email_verified=False,
        is_active=False,
    )

    cache.set(
        f'register_otp_cooldown:{user.email}',
        True,
        timeout=60,
    )

    response = client.post(
        RESEND_REGISTER_OTP_URL,
        {
            "email": "testuser@example.com",
        },
        format="json",
    )

    assert response.status_code == 429

    data = response.json()
    assert "detail" in data
    assert "đợi" in data["detail"]


@pytest.mark.django_db
def test_resend_register_otp_nonexistent_user():
    client = APIClient()

    response = client.post(
        RESEND_REGISTER_OTP_URL,
        {
            "email": "nonexistent@example.com",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data


@pytest.mark.django_db
def test_resend_register_otp_invalid_email():
    client = APIClient()

    response = client.post(
        RESEND_REGISTER_OTP_URL,
        {
            "email": "invalid-email",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "email" in data
