import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember, Activity


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_household_activities_url(household_id):
    return f"/api/households/{household_id}/activities/"


@pytest.mark.django_db
def test_list_household_activities_success():
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

    Activity.objects.create(
        household=household,
        actor=owner,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Owner joined household",
    )

    Activity.objects.create(
        household=household,
        actor=owner,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Another activity",
    )

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_household_activities_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert len(data["results"]) >= 2


@pytest.mark.django_db
def test_list_household_activities_empty():
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

    response = client.get(
        get_household_activities_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert len(data["results"]) == 0


@pytest.mark.django_db
def test_list_household_activities_unauthorized():
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

    response = client.get(
        get_household_activities_url(household.id),
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_household_activities_not_member():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
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

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_household_activities_url(household.id),
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_list_household_activities_pagination():
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

    for i in range(25):
        Activity.objects.create(
            household=household,
            actor=owner,
            activity_type=Activity.ActivityType.MEMBER_JOINED,
            title=f"Activity {i}",
        )

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_household_activities_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert "count" in data
    assert data["count"] == 25
    assert len(data["results"]) <= 20


@pytest.mark.django_db
def test_list_household_activities_as_member():
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

    Activity.objects.create(
        household=household,
        actor=owner,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Owner activity",
    )

    Activity.objects.create(
        household=household,
        actor=member,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Member activity",
    )

    token = get_auth_header(member)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_household_activities_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
