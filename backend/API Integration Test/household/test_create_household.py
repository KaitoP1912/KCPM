import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember


CREATE_HOUSEHOLD_URL = "/api/households/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_create_household_success():
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

    response = client.post(
        CREATE_HOUSEHOLD_URL,
        {
            "name": "New Household",
            "description": "Test description",
        },
        format="json",
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["name"] == "New Household"
    assert data["description"] == "Test description"
    assert data["owner"] == user.id
    assert "invite_code" in data
    assert "members" in data

    household = Household.objects.get(
        id=data["id"]
    )
    assert household.owner == user
    assert HouseholdMember.objects.filter(
        household=household,
        user=user,
        role=HouseholdMember.Role.OWNER,
    ).exists()


@pytest.mark.django_db
def test_create_household_missing_name():
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

    response = client.post(
        CREATE_HOUSEHOLD_URL,
        {
            "description": "Test description",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "name" in data


@pytest.mark.django_db
def test_create_household_empty_name():
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

    response = client.post(
        CREATE_HOUSEHOLD_URL,
        {
            "name": "",
            "description": "Test description",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "name" in data


@pytest.mark.django_db
def test_create_household_unauthenticated():
    client = APIClient()

    response = client.post(
        CREATE_HOUSEHOLD_URL,
        {
            "name": "New Household",
            "description": "Test description",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_household_without_description():
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

    response = client.post(
        CREATE_HOUSEHOLD_URL,
        {
            "name": "New Household",
        },
        format="json",
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "New Household"
    assert "id" in data
