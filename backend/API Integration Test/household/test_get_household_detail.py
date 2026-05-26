import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from households.models import Household, HouseholdMember


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_household_detail_url(household_id):
    return f"/api/households/{household_id}/"


@pytest.mark.django_db
def test_get_household_detail_success():
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
        description="Test description",
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
        get_household_detail_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(household.id)
    assert data["name"] == "Test Household"
    assert data["description"] == "Test description"
    assert data["owner"] == user.id
    assert "members" in data
    assert len(data["members"]) >= 1


@pytest.mark.django_db
def test_get_household_detail_not_found():
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

    fake_id = uuid.uuid4()

    response = client.get(
        get_household_detail_url(fake_id),
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_get_household_detail_unauthenticated():
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

    response = client.get(
        get_household_detail_url(household.id),
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_household_detail_forbidden():
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

    household = Household.objects.create(
        name="User1 Household",
        owner=user1,
    )

    HouseholdMember.objects.create(
        household=household,
        user=user1,
        role=HouseholdMember.Role.OWNER,
    )

    token = get_auth_header(user2)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_household_detail_url(household.id),
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_get_household_detail_as_member():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    member = user_model.objects.create_user(
        email="member@example.com",
        username="member",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=owner,
    )

    HouseholdMember.objects.create(
        household=household,
        user=owner,
        role=HouseholdMember.Role.OWNER,
    )

    HouseholdMember.objects.create(
        household=household,
        user=member,
        role=HouseholdMember.Role.MEMBER,
    )

    token = get_auth_header(member)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_household_detail_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(household.id)
    assert len(data["members"]) == 2
