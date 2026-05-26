import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_add_member_url(household_id):
    return f"/api/households/{household_id}/members/add/"


@pytest.mark.django_db
def test_add_member_success():
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

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        get_add_member_url(household.id),
        {
            "email": "member@example.com",
        },
        format="json",
    )

    assert response.status_code == 201

    data = response.json()
    assert "message" in data
    assert "household" in data

    membership = HouseholdMember.objects.filter(
        household=household,
        user=new_member,
    ).first()
    assert membership is not None
    assert membership.role == HouseholdMember.Role.MEMBER


@pytest.mark.django_db
def test_add_member_missing_email():
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
        get_add_member_url(household.id),
        {},
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_add_member_not_found_user():
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
        get_add_member_url(household.id),
        {
            "email": "nonexistent@example.com",
        },
        format="json",
    )

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_add_member_already_member():
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

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        get_add_member_url(household.id),
        {
            "email": "member@example.com",
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_add_member_not_owner():
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

    new_user = user_model.objects.create_user(
        email="newuser@example.com",
        username="newuser",
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

    response = client.post(
        get_add_member_url(household.id),
        {
            "email": "newuser@example.com",
        },
        format="json",
    )

    assert response.status_code == 403

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_add_member_unauthenticated():
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

    response = client.post(
        get_add_member_url(household.id),
        {
            "email": "member@example.com",
        },
        format="json",
    )

    assert response.status_code == 401
