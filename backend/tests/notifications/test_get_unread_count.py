import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from notifications.models import Notification


UNREAD_COUNT_URL = "/api/notifications/unread-count/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_get_unread_count_success():
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

    Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="Notification 1",
        is_read=False,
    )

    Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.DEBT_CREATED,
        title="Notification 2",
        is_read=False,
    )

    Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.PAYMENT_RECEIVED,
        title="Notification 3",
        is_read=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        UNREAD_COUNT_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "unread_count" in data
    assert data["unread_count"] == 2


@pytest.mark.django_db
def test_get_unread_count_zero():
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
        UNREAD_COUNT_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "unread_count" in data
    assert data["unread_count"] == 0


@pytest.mark.django_db
def test_get_unread_count_all_read():
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

    Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="Notification 1",
        is_read=True,
    )

    Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.DEBT_CREATED,
        title="Notification 2",
        is_read=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        UNREAD_COUNT_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "unread_count" in data
    assert data["unread_count"] == 0


@pytest.mark.django_db
def test_get_unread_count_unauthenticated():
    client = APIClient()

    response = client.get(
        UNREAD_COUNT_URL,
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_unread_count_only_user_notifications():
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

    Notification.objects.create(
        recipient=user1,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="Notification for user1",
        is_read=False,
    )

    Notification.objects.create(
        recipient=user1,
        actor=actor,
        notification_type=Notification.NotificationType.DEBT_CREATED,
        title="Another notification for user1",
        is_read=False,
    )

    Notification.objects.create(
        recipient=user2,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="Notification for user2",
        is_read=False,
    )

    token = get_auth_header(user1)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        UNREAD_COUNT_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "unread_count" in data
    assert data["unread_count"] == 2
