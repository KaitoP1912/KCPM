import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember
from expenses.models import Debt


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_kick_member_url(household_id, member_id):
    return f"/api/households/{household_id}/members/{member_id}/kick/"


@pytest.mark.django_db
def test_kick_member_success():
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

    owner_membership = HouseholdMember.objects.create(
        household=household,
        user=owner,
        role=HouseholdMember.Role.OWNER,
    )

    member_membership = HouseholdMember.objects.create(
        household=household,
        user=member,
        role=HouseholdMember.Role.MEMBER,
    )

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.delete(
        get_kick_member_url(
            household.id,
            member_membership.id,
        ),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "household" in data

    membership_exists = HouseholdMember.objects.filter(
        id=member_membership.id,
    ).exists()
    assert membership_exists is False


@pytest.mark.django_db
def test_kick_member_not_found():
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

    import uuid
    fake_member_id = uuid.uuid4()

    response = client.delete(
        get_kick_member_url(
            household.id,
            fake_member_id,
        ),
        format="json",
    )

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_kick_member_not_owner():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    member1 = user_model.objects.create_user(
        email="member1@example.com",
        username="member1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    member2 = user_model.objects.create_user(
        email="member2@example.com",
        username="member2",
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
        user=member1,
        role=HouseholdMember.Role.MEMBER,
    )

    member2_membership = HouseholdMember.objects.create(
        household=household,
        user=member2,
        role=HouseholdMember.Role.MEMBER,
    )

    token = get_auth_header(member1)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.delete(
        get_kick_member_url(
            household.id,
            member2_membership.id,
        ),
        format="json",
    )

    assert response.status_code == 403

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_kick_member_self():
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

    owner_membership = HouseholdMember.objects.create(
        household=household,
        user=owner,
        role=HouseholdMember.Role.OWNER,
    )

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.delete(
        get_kick_member_url(
            household.id,
            owner_membership.id,
        ),
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_kick_member_unauthenticated():
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

    member_membership = HouseholdMember.objects.create(
        household=household,
        user=member,
        role=HouseholdMember.Role.MEMBER,
    )

    response = client.delete(
        get_kick_member_url(
            household.id,
            member_membership.id,
        ),
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_kick_member_household_not_found():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    import uuid
    fake_household_id = uuid.uuid4()
    fake_member_id = uuid.uuid4()

    response = client.delete(
        get_kick_member_url(
            fake_household_id,
            fake_member_id,
        ),
        format="json",
    )

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
