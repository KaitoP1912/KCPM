import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember


JOIN_HOUSEHOLD_URL = "/api/households/join/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_join_household_by_invite_code_success():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    new_member = user_model.objects.create_user(
        email="newmember@example.com",
        username="newmember",
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

    token = get_auth_header(new_member)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        JOIN_HOUSEHOLD_URL,
        {
            "invite_code": household.invite_code,
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "household" in data
    assert data["household"]["name"] == "Test Household"

    membership = HouseholdMember.objects.filter(
        household=household,
        user=new_member,
    ).first()
    assert membership is not None
    assert membership.role == HouseholdMember.Role.MEMBER


@pytest.mark.django_db
def test_join_household_invalid_invite_code():
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
        JOIN_HOUSEHOLD_URL,
        {
            "invite_code": "INVALID_CODE_123",
        },
        format="json",
    )

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_join_household_already_member():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
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

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        JOIN_HOUSEHOLD_URL,
        {
            "invite_code": household.invite_code,
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "đã ở trong nhóm" in data["detail"]


@pytest.mark.django_db
def test_join_household_missing_invite_code():
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
        JOIN_HOUSEHOLD_URL,
        {},
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "invite_code" in data


@pytest.mark.django_db
def test_join_household_unauthenticated():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
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

    response = client.post(
        JOIN_HOUSEHOLD_URL,
        {
            "invite_code": household.invite_code,
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_join_household_empty_invite_code():
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
        JOIN_HOUSEHOLD_URL,
        {
            "invite_code": "",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "invite_code" in data
