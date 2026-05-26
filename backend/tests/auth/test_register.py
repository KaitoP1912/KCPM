import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


REGISTER_URL = "/api/auth/register/"


@pytest.mark.django_db
def test_register_success():
    client = APIClient()

    response = client.post(
        REGISTER_URL,
        {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "phone_number": "+84123456789",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert response.status_code == 201

    data = response.json()
    assert "message" in data
    assert "email" in data
    assert data["email"] == "newuser@example.com"


@pytest.mark.django_db
def test_register_missing_email():
    client = APIClient()

    response = client.post(
        REGISTER_URL,
        {
            "username": "newuser",
            "full_name": "New User",
            "phone_number": "+84123456789",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "email" in data


@pytest.mark.django_db
def test_register_missing_password():
    client = APIClient()

    response = client.post(
        REGISTER_URL,
        {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "phone_number": "+84123456789",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "password" in data


@pytest.mark.django_db
def test_register_missing_username():
    client = APIClient()

    response = client.post(
        REGISTER_URL,
        {
            "email": "newuser@example.com",
            "full_name": "New User",
            "phone_number": "+84123456789",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "username" in data


@pytest.mark.django_db
def test_register_short_password():
    client = APIClient()

    response = client.post(
        REGISTER_URL,
        {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "phone_number": "+84123456789",
            "password": "Short1",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "password" in data


@pytest.mark.django_db
def test_register_duplicate_verified_email():
    client = APIClient()
    user_model = get_user_model()

    user_model.objects.create_user(
        email="existing@example.com",
        username="existing",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    response = client.post(
        REGISTER_URL,
        {
            "email": "existing@example.com",
            "username": "newuser",
            "full_name": "New User",
            "phone_number": "+84123456789",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "email" in data


@pytest.mark.django_db
def test_register_invalid_email():
    client = APIClient()

    response = client.post(
        REGISTER_URL,
        {
            "email": "invalid-email",
            "username": "newuser",
            "full_name": "New User",
            "phone_number": "+84123456789",
            "password": "StrongPass123",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "email" in data
