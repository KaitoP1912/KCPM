import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


VIEW_PROFILE_URL = "/api/auth/profile/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_view_profile_success():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        full_name="John Doe",
        phone_number="1234567890",
        bank_name="Vietcombank",
        bank_account_number="123456789",
        bank_account_holder="John Doe",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        VIEW_PROFILE_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == "user@example.com"
    assert data["username"] == "user1"
    assert data["full_name"] == "John Doe"
    assert data["phone_number"] == "1234567890"
    assert data["bank_name"] == "Vietcombank"
    assert data["bank_account_number"] == "123456789"
    assert data["bank_account_holder"] == "John Doe"
    assert data["email_verified"] is True


@pytest.mark.django_db
def test_view_profile_minimal_data():
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

    response = client.get(
        VIEW_PROFILE_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == "user@example.com"
    assert data["username"] == "user1"
    assert "full_name" in data
    assert "phone_number" in data
    assert "avatar_url" in data


@pytest.mark.django_db
def test_view_profile_unauthenticated():
    client = APIClient()

    response = client.get(
        VIEW_PROFILE_URL,
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_view_profile_with_avatar():
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

    response = client.get(
        VIEW_PROFILE_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "avatar" in data
    assert "avatar_url" in data


@pytest.mark.django_db
def test_view_profile_auth_provider():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        auth_provider="email",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        VIEW_PROFILE_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "auth_provider" in data
    assert data["auth_provider"] == "email"
