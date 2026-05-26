import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from notifications.models import Notification


MARK_ALL_READ_URL = "/api/notifications/mark-all-read/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_mark_all_notifications_as_read_success():
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

    response = client.patch(
        MARK_ALL_READ_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    unread_count = Notification.objects.filter(
        recipient=user,
        is_read=False,
    ).count()
    assert unread_count == 0


@pytest.mark.django_db
def test_mark_all_notifications_as_read_empty_list():
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

    response = client.patch(
        MARK_ALL_READ_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data


@pytest.mark.django_db
def test_mark_all_notifications_as_read_already_all_read():
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

    response = client.patch(
        MARK_ALL_READ_URL,
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data


@pytest.mark.django_db
def test_mark_all_notifications_as_read_unauthenticated():
    client = APIClient()

    response = client.patch(
        MARK_ALL_READ_URL,
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_mark_all_notifications_as_read_only_user_notifications():
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
        recipient=user2,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="Notification for user2",
        is_read=False,
    )

    token = get_auth_header(user1)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.patch(
        MARK_ALL_READ_URL,
        format="json",
    )

    assert response.status_code == 200

    user1_unread = Notification.objects.filter(
        recipient=user1,
        is_read=False,
    ).count()
    assert user1_unread == 0

    user2_unread = Notification.objects.filter(
        recipient=user2,
        is_read=False,
    ).count()
    assert user2_unread == 1
