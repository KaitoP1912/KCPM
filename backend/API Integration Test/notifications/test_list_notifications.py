import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember
from notifications.models import Notification


LIST_NOTIFICATIONS_URL = "/api/notifications/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_list_notifications_success():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    actor = user_model.objects.create_user(
        email="actor@example.com",
        username="actor",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=actor,
    )

    HouseholdMember.objects.create(
        household=household,
        user=actor,
        role=HouseholdMember.Role.OWNER,
    )

    HouseholdMember.objects.create(
        household=household,
        user=user,
        role=HouseholdMember.Role.MEMBER,
    )

    Notification.objects.create(
        recipient=user,
        actor=actor,
        household=household,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="You were added to a group",
        is_read=False,
    )

    Notification.objects.create(
        recipient=user,
        actor=actor,
        household=household,
        notification_type=Notification.NotificationType.DEBT_CREATED,
        title="New debt created",
        amount=50000,
        is_read=False,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        LIST_NOTIFICATIONS_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert len(data["results"]) == 2


@pytest.mark.django_db
def test_list_notifications_empty():
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
        LIST_NOTIFICATIONS_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


@pytest.mark.django_db
def test_list_notifications_unauthenticated():
    client = APIClient()

    response = client.get(
        LIST_NOTIFICATIONS_URL,
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_notifications_only_user_notifications():
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

    actor = user_model.objects.create_user(
        email="actor@example.com",
        username="actor",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=actor,
    )

    HouseholdMember.objects.create(
        household=household,
        user=actor,
        role=HouseholdMember.Role.OWNER,
    )

    Notification.objects.create(
        recipient=user1,
        actor=actor,
        household=household,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="You were added to a group",
        is_read=False,
    )

    Notification.objects.create(
        recipient=user2,
        actor=actor,
        household=household,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="You were added to a group",
        is_read=False,
    )

    token = get_auth_header(user1)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        LIST_NOTIFICATIONS_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["recipient"] == user1.id


@pytest.mark.django_db
def test_list_notifications_pagination():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    actor = user_model.objects.create_user(
        email="actor@example.com",
        username="actor",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    for i in range(25):
        Notification.objects.create(
            recipient=user,
            actor=actor,
            notification_type=Notification.NotificationType.ADDED_TO_GROUP,
            title=f"Notification {i}",
            is_read=False,
        )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        LIST_NOTIFICATIONS_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert "count" in data
    assert data["count"] == 25
    assert len(data["results"]) <= 20


@pytest.mark.django_db
def test_list_notifications_ordered_by_created_at():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    actor = user_model.objects.create_user(
        email="actor@example.com",
        username="actor",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    notification1 = Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="First notification",
        is_read=False,
    )

    notification2 = Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.DEBT_CREATED,
        title="Second notification",
        is_read=False,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        LIST_NOTIFICATIONS_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
    assert data["results"][0]["id"] == str(notification2.id)
    assert data["results"][1]["id"] == str(notification1.id)
