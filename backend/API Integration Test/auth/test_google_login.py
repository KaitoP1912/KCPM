import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch


GOOGLE_LOGIN_URL = "/api/auth/google-login/"


@pytest.mark.django_db
def test_google_login_success_new_user():
    client = APIClient()

    mock_idinfo = {
        "email": "newuser@gmail.com",
        "name": "New User",
    }

    with patch(
        'accounts.views.id_token.verify_oauth2_token',
        return_value=mock_idinfo,
    ):
        response = client.post(
            GOOGLE_LOGIN_URL,
            {
                "token": "valid_google_token",
            },
            format="json",
        )

    assert response.status_code == 200

    data = response.json()
    assert "access" in data
    assert "refresh" in data
    assert "user" in data
    assert data["user"]["email"] == "newuser@gmail.com"

    user_model = get_user_model()
    user = user_model.objects.get(
        email="newuser@gmail.com"
    )
    assert user.auth_provider == "google"
    assert user.email_verified is True
    assert user.is_active is True


@pytest.mark.django_db
def test_google_login_success_existing_user():
    client = APIClient()
    user_model = get_user_model()

    existing_user = user_model.objects.create_user(
        email="existing@gmail.com",
        username="existing",
        password="StrongPass123",
        auth_provider="google",
        email_verified=True,
        is_active=True,
    )

    mock_idinfo = {
        "email": "existing@gmail.com",
        "name": "Existing User",
    }

    with patch(
        'accounts.views.id_token.verify_oauth2_token',
        return_value=mock_idinfo,
    ):
        response = client.post(
            GOOGLE_LOGIN_URL,
            {
                "token": "valid_google_token",
            },
            format="json",
        )

    assert response.status_code == 200

    data = response.json()
    assert "access" in data
    assert "refresh" in data
    assert "user" in data
    assert data["user"]["email"] == "existing@gmail.com"


@pytest.mark.django_db
def test_google_login_missing_token():
    client = APIClient()

    response = client.post(
        GOOGLE_LOGIN_URL,
        {},
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "token" in data["detail"]


@pytest.mark.django_db
def test_google_login_invalid_token():
    client = APIClient()

    with patch(
        'accounts.views.id_token.verify_oauth2_token',
        side_effect=Exception("Invalid token"),
    ), patch(
        'accounts.views.pyrequests.get',
        side_effect=Exception("Invalid token"),
    ):
        response = client.post(
            GOOGLE_LOGIN_URL,
            {
                "token": "invalid_token",
            },
            format="json",
        )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_google_login_no_email_in_token():
    client = APIClient()

    mock_idinfo = {
        "name": "User Without Email",
    }

    with patch(
        'accounts.views.id_token.verify_oauth2_token',
        return_value=mock_idinfo,
    ):
        response = client.post(
            GOOGLE_LOGIN_URL,
            {
                "token": "token_without_email",
            },
            format="json",
        )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "email" in data["detail"]


@pytest.mark.django_db
def test_google_login_empty_token():
    client = APIClient()

    response = client.post(
        GOOGLE_LOGIN_URL,
        {
            "token": "",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
