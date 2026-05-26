import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember


LIST_HOUSEHOLDS_URL = "/api/households/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_list_households_success():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=user,
    )

    HouseholdMember.objects.create(
        household=household,
        user=user,
        role=HouseholdMember.Role.OWNER,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        LIST_HOUSEHOLDS_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Test Household"
    assert "id" in data[0]
    assert "members" in data[0]


@pytest.mark.django_db
def test_list_households_empty():
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
        LIST_HOUSEHOLDS_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.django_db
def test_list_households_multiple():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    for i in range(3):
        household = Household.objects.create(
            name=f"Household {i}",
            owner=user,
        )

        HouseholdMember.objects.create(
            household=household,
            user=user,
            role=HouseholdMember.Role.OWNER,
        )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        LIST_HOUSEHOLDS_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3


@pytest.mark.django_db
def test_list_households_unauthenticated():
    client = APIClient()

    response = client.get(
        LIST_HOUSEHOLDS_URL,
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_households_only_user_households():
    client = APIClient()
    user_model = get_user_model()

    user1 = user_model.objects.create_user(
        email="user1@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    user2 = user_model.objects.create_user(
        email="user2@example.com",
        username="user2",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household1 = Household.objects.create(
        name="User1 Household",
        owner=user1,
    )

    HouseholdMember.objects.create(
        household=household1,
        user=user1,
        role=HouseholdMember.Role.OWNER,
    )

    household2 = Household.objects.create(
        name="User2 Household",
        owner=user2,
    )

    HouseholdMember.objects.create(
        household=household2,
        user=user2,
        role=HouseholdMember.Role.OWNER,
    )

    token = get_auth_header(user1)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        LIST_HOUSEHOLDS_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "User1 Household"
