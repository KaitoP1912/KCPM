import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient


VERIFY_REGISTER_OTP_URL = "/api/auth/verify-register-otp/"


@pytest.mark.django_db
def test_verify_register_otp_success():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="testuser@example.com",
        username="testuser",
        password="StrongPass123",
        email_verified=False,
        is_active=False,
    )

    otp = "123456"
    cache.set(
        f'register_otp:{user.email}',
        otp,
        timeout=600,
    )

    response = client.post(
        VERIFY_REGISTER_OTP_URL,
        {
            "email": "testuser@example.com",
            "otp": otp,
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    user.refresh_from_db()
    assert user.email_verified is True
    assert user.is_active is True


@pytest.mark.django_db
def test_verify_register_otp_missing_email():
    client = APIClient()

    response = client.post(
        VERIFY_REGISTER_OTP_URL,
        {
            "otp": "123456",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "email" in data


@pytest.mark.django_db
def test_verify_register_otp_missing_otp():
    client = APIClient()

    response = client.post(
        VERIFY_REGISTER_OTP_URL,
        {
            "email": "testuser@example.com",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "otp" in data


@pytest.mark.django_db
def test_verify_register_otp_incorrect_otp():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="testuser@example.com",
        username="testuser",
        password="StrongPass123",
        email_verified=False,
        is_active=False,
    )

    otp = "123456"
    cache.set(
        f'register_otp:{user.email}',
        otp,
        timeout=600,
    )

    response = client.post(
        VERIFY_REGISTER_OTP_URL,
        {
            "email": "testuser@example.com",
            "otp": "999999",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "không chính xác" in data["detail"]


@pytest.mark.django_db
def test_verify_register_otp_expired():
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
        VERIFY_REGISTER_OTP_URL,
        {
            "email": "testuser@example.com",
            "otp": "123456",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "hết hạn" in data["detail"]


@pytest.mark.django_db
def test_verify_register_otp_nonexistent_user():
    client = APIClient()

    otp = "123456"
    cache.set(
        'register_otp:nonexistent@example.com',
        otp,
        timeout=600,
    )

    response = client.post(
        VERIFY_REGISTER_OTP_URL,
        {
            "email": "nonexistent@example.com",
            "otp": otp,
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_verify_register_otp_invalid_otp_length():
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
        VERIFY_REGISTER_OTP_URL,
        {
            "email": "testuser@example.com",
            "otp": "12345",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "otp" in data
