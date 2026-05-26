import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


LOGIN_URL = "/api/auth/login/"
REFRESH_URL = "/api/auth/refresh/"


@pytest.mark.django_db
def test_refresh_token_success():
    client = APIClient()
    user_model = get_user_model()
    password = "StrongPass123"

    user_model.objects.create_user(
        email="student@example.com",
        username="student1",
        password=password,
        email_verified=True,
        is_active=True,
    )

    login_response = client.post(
        LOGIN_URL,
        {
            "email": "student@example.com",
            "password": password,
        },
        format="json",
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "refresh" in login_data

    response = client.post(
        REFRESH_URL,
        {
            "refresh": login_data["refresh"],
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "access" in data


@pytest.mark.django_db
def test_refresh_token_invalid_token():
    client = APIClient()

    response = client.post(
        REFRESH_URL,
        {
            "refresh": "invalid.refresh.token",
        },
        format="json",
    )

    assert response.status_code == 401

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_refresh_token_missing_field():
    client = APIClient()

    response = client.post(
        REFRESH_URL,
        {},
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "refresh" in data
