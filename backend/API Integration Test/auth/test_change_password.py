import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


LOGIN_URL = "/api/auth/login/"
CHANGE_PASSWORD_URL = "/api/auth/change-password/"


@pytest.mark.django_db
def test_change_password_success():
    client = APIClient()
    user_model = get_user_model()
    old_password = "StrongPass123"
    new_password = "NewStrongPass123"

    user = user_model.objects.create_user(
        email="student@example.com",
        username="student1",
        password=old_password,
        email_verified=True,
        is_active=True,
    )

    login_response = client.post(
        LOGIN_URL,
        {
            "email": "student@example.com",
            "password": old_password,
        },
        format="json",
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access" in login_data

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {login_data['access']}"
    )

    response = client.post(
        CHANGE_PASSWORD_URL,
        {
            "old_password": old_password,
            "new_password": new_password,
            "confirm_password": new_password,
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    user.refresh_from_db()
    assert user.check_password(new_password) is True


@pytest.mark.django_db
def test_change_password_wrong_old_password():
    client = APIClient()
    user_model = get_user_model()

    user_model.objects.create_user(
        email="student@example.com",
        username="student1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    login_response = client.post(
        LOGIN_URL,
        {
            "email": "student@example.com",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert login_response.status_code == 200
    login_data = login_response.json()

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {login_data['access']}"
    )

    response = client.post(
        CHANGE_PASSWORD_URL,
        {
            "old_password": "WrongPass123",
            "new_password": "NewStrongPass123",
            "confirm_password": "NewStrongPass123",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_change_password_confirm_mismatch():
    client = APIClient()
    user_model = get_user_model()

    user_model.objects.create_user(
        email="student@example.com",
        username="student1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    login_response = client.post(
        LOGIN_URL,
        {
            "email": "student@example.com",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert login_response.status_code == 200
    login_data = login_response.json()

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {login_data['access']}"
    )

    response = client.post(
        CHANGE_PASSWORD_URL,
        {
            "old_password": "StrongPass123",
            "new_password": "NewStrongPass123",
            "confirm_password": "DifferentPass123",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "confirm_password" in data
