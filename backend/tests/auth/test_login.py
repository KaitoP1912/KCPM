import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


LOGIN_URL = "/api/auth/login/"


@pytest.mark.django_db
def test_login_success():
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

    response = client.post(
        LOGIN_URL,
        {
            "email": "student@example.com",
            "password": password,
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "access" in data
    assert "refresh" in data


@pytest.mark.django_db
def test_login_wrong_password():
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
        LOGIN_URL,
        {
            "email": "student@example.com",
            "password": "WrongPass123",
        },
        format="json",
    )

    assert response.status_code == 401

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_login_missing_email():
    client = APIClient()

    response = client.post(
        LOGIN_URL,
        {
            "password": "StrongPass123",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "email" in data


@pytest.mark.django_db
def test_login_missing_password():
    client = APIClient()

    response = client.post(
        LOGIN_URL,
        {
            "email": "student@example.com",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "password" in data
