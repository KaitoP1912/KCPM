import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient


RESET_PASSWORD_URL = "/api/auth/reset-password/"


@pytest.mark.django_db
def test_reset_password_success():
    client = APIClient()
    user_model = get_user_model()
    email = "student@example.com"
    otp = "123456"

    user_model.objects.create_user(
        email=email,
        username="student1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    cache.set(
        f"forgot_password_otp:{email}",
        otp,
        timeout=600,
    )

    response = client.post(
        RESET_PASSWORD_URL,
        {
            "email": email,
            "otp": otp,
            "new_password": "NewStrongPass123",
            "confirm_password": "NewStrongPass123",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data


@pytest.mark.django_db
def test_reset_password_invalid_otp():
    client = APIClient()
    user_model = get_user_model()
    email = "student@example.com"

    user_model.objects.create_user(
        email=email,
        username="student1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    cache.set(
        f"forgot_password_otp:{email}",
        "123456",
        timeout=600,
    )

    response = client.post(
        RESET_PASSWORD_URL,
        {
            "email": email,
            "otp": "000000",
            "new_password": "NewStrongPass123",
            "confirm_password": "NewStrongPass123",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_reset_password_confirm_mismatch():
    client = APIClient()
    user_model = get_user_model()
    email = "student@example.com"
    otp = "123456"

    user_model.objects.create_user(
        email=email,
        username="student1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    cache.set(
        f"forgot_password_otp:{email}",
        otp,
        timeout=600,
    )

    response = client.post(
        RESET_PASSWORD_URL,
        {
            "email": email,
            "otp": otp,
            "new_password": "NewStrongPass123",
            "confirm_password": "DifferentPass123",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "confirm_password" in data
