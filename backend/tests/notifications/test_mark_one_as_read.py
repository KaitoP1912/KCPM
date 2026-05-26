import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from notifications.models import Notification


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_mark_read_url(notification_id):
    return f"/api/notifications/{notification_id}/read/"


@pytest.mark.django_db
def test_mark_one_notification_as_read_success():
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

    notification = Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="You were added to a group",
        is_read=False,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.patch(
        get_mark_read_url(notification.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    notification.refresh_from_db()
    assert notification.is_read is True


@pytest.mark.django_db
def test_mark_one_notification_as_read_not_found():
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

    response = client.patch(
        get_mark_read_url(fake_id),
        format="json",
    )

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_mark_one_notification_as_read_not_recipient():
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

    notification = Notification.objects.create(
        recipient=user1,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="Notification for user1",
        is_read=False,
    )

    token = get_auth_header(user2)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.patch(
        get_mark_read_url(notification.id),
        format="json",
    )

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data

    notification.refresh_from_db()
    assert notification.is_read is False


@pytest.mark.django_db
def test_mark_one_notification_as_read_unauthenticated():
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

    notification = Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="Notification",
        is_read=False,
    )

    response = client.patch(
        get_mark_read_url(notification.id),
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_mark_one_notification_as_read_already_read():
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

    notification = Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.ADDED_TO_GROUP,
        title="Already read notification",
        is_read=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.patch(
        get_mark_read_url(notification.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    notification.refresh_from_db()
    assert notification.is_read is True


@pytest.mark.django_db
def test_mark_one_notification_as_read_multiple_notifications():
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
        title="Notification 1",
        is_read=False,
    )

    notification2 = Notification.objects.create(
        recipient=user,
        actor=actor,
        notification_type=Notification.NotificationType.DEBT_CREATED,
        title="Notification 2",
        is_read=False,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.patch(
        get_mark_read_url(notification1.id),
        format="json",
    )

    assert response.status_code == 200

    notification1.refresh_from_db()
    notification2.refresh_from_db()
    assert notification1.is_read is True
    assert notification2.is_read is False
