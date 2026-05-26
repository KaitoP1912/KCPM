import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient


FORGOT_PASSWORD_URL = "/api/auth/forgot-password/"


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
def test_forgot_password_success():
    client = APIClient()
    user_model = get_user_model()

    user_model.objects.create_user(
        email="student@example.com",
        username="student1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    response = client.post(
        FORGOT_PASSWORD_URL,
        {
            "email": "student@example.com",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data


@pytest.mark.django_db
def test_forgot_password_missing_email():
    client = APIClient()

    response = client.post(
        FORGOT_PASSWORD_URL,
        {},
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "email" in data


@pytest.mark.django_db
def test_forgot_password_invalid_email_format():
    client = APIClient()

    response = client.post(
        FORGOT_PASSWORD_URL,
        {
            "email": "not-an-email",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "email" in data
