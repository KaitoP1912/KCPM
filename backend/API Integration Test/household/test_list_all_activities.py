import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember, Activity


ALL_ACTIVITIES_URL = "/api/households/activities/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_list_all_activities_success():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household1 = Household.objects.create(
        name="Household 1",
        owner=user,
    )

    HouseholdMember.objects.create(
        household=household1,
        user=user,
        role=HouseholdMember.Role.OWNER,
    )

    household2 = Household.objects.create(
        name="Household 2",
        owner=user,
    )

    HouseholdMember.objects.create(
        household=household2,
        user=user,
        role=HouseholdMember.Role.OWNER,
    )

    Activity.objects.create(
        household=household1,
        actor=user,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Activity in household 1",
    )

    Activity.objects.create(
        household=household2,
        actor=user,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Activity in household 2",
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        ALL_ACTIVITIES_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert len(data["results"]) >= 2


@pytest.mark.django_db
def test_list_all_activities_empty():
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
        ALL_ACTIVITIES_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert len(data["results"]) == 0


@pytest.mark.django_db
def test_list_all_activities_unauthenticated():
    client = APIClient()

    response = client.get(
        ALL_ACTIVITIES_URL,
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_all_activities_multiple_households():
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

    household1 = Household.objects.create(
        name="Household 1",
        owner=owner,
    )

    HouseholdMember.objects.create(
        household=household1,
        user=owner,
        role=HouseholdMember.Role.OWNER,
    )

    household2 = Household.objects.create(
        name="Household 2",
        owner=owner,
    )

    HouseholdMember.objects.create(
        household=household2,
        user=owner,
        role=HouseholdMember.Role.OWNER,
    )

    HouseholdMember.objects.create(
        household=household2,
        user=member,
        role=HouseholdMember.Role.MEMBER,
    )

    Activity.objects.create(
        household=household1,
        actor=owner,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Activity in household 1",
    )

    Activity.objects.create(
        household=household2,
        actor=member,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Member activity in household 2",
    )

    Activity.objects.create(
        household=household2,
        actor=owner,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Owner activity in household 2",
    )

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        ALL_ACTIVITIES_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3


@pytest.mark.django_db
def test_list_all_activities_pagination():
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

    for i in range(25):
        Activity.objects.create(
            household=household,
            actor=user,
            activity_type=Activity.ActivityType.MEMBER_JOINED,
            title=f"Activity {i}",
        )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        ALL_ACTIVITIES_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert "count" in data
    assert data["count"] == 25
    assert len(data["results"]) <= 20


@pytest.mark.django_db
def test_list_all_activities_only_member_households():
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

    Activity.objects.create(
        household=household1,
        actor=user1,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Activity in household 1",
    )

    Activity.objects.create(
        household=household2,
        actor=user2,
        activity_type=Activity.ActivityType.MEMBER_JOINED,
        title="Activity in household 2",
    )

    token = get_auth_header(user1)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        ALL_ACTIVITIES_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert "Activity in household 1" in data["results"][0]["title"]
