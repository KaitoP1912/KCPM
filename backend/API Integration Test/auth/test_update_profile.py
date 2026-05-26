import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


UPDATE_PROFILE_URL = "/api/auth/profile/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_update_profile_full_name_success():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        full_name="Old Name",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.put(
        UPDATE_PROFILE_URL,
        {
            "full_name": "New Name",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == "New Name"

    user.refresh_from_db()
    assert user.full_name == "New Name"


@pytest.mark.django_db
def test_update_profile_phone_number_success():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        phone_number="1111111111",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.put(
        UPDATE_PROFILE_URL,
        {
            "phone_number": "9999999999",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["phone_number"] == "9999999999"

    user.refresh_from_db()
    assert user.phone_number == "9999999999"


@pytest.mark.django_db
def test_update_profile_bank_details_success():
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

    response = client.put(
        UPDATE_PROFILE_URL,
        {
            "bank_name": "Vietcombank",
            "bank_account_number": "123456789",
            "bank_account_holder": "John Doe",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["bank_name"] == "Vietcombank"
    assert data["bank_account_number"] == "123456789"
    assert data["bank_account_holder"] == "John Doe"

    user.refresh_from_db()
    assert user.bank_name == "Vietcombank"
    assert user.bank_account_number == "123456789"
    assert user.bank_account_holder == "John Doe"


@pytest.mark.django_db
def test_update_profile_partial_update():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        full_name="Original Name",
        phone_number="1111111111",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.patch(
        UPDATE_PROFILE_URL,
        {
            "full_name": "Updated Name",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["phone_number"] == "1111111111"

    user.refresh_from_db()
    assert user.full_name == "Updated Name"
    assert user.phone_number == "1111111111"


@pytest.mark.django_db
def test_update_profile_cannot_modify_email():
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

    response = client.put(
        UPDATE_PROFILE_URL,
        {
            "email": "newemail@example.com",
            "full_name": "Updated Name",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "user@example.com"

    user.refresh_from_db()
    assert user.email == "user@example.com"


@pytest.mark.django_db
def test_update_profile_cannot_modify_username():
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

    response = client.put(
        UPDATE_PROFILE_URL,
        {
            "username": "newusername",
            "full_name": "Updated Name",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "user1"

    user.refresh_from_db()
    assert user.username == "user1"


@pytest.mark.django_db
def test_update_profile_unauthenticated():
    client = APIClient()

    response = client.put(
        UPDATE_PROFILE_URL,
        {
            "full_name": "Updated Name",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_update_profile_empty_update():
    client = APIClient()
    user_model = get_user_model()

    user = user_model.objects.create_user(
        email="user@example.com",
        username="user1",
        password="StrongPass123",
        full_name="Original Name",
        email_verified=True,
        is_active=True,
    )

    token = get_auth_header(user)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.put(
        UPDATE_PROFILE_URL,
        {},
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == "Original Name"

    user.refresh_from_db()
    assert user.full_name == "Original Name"


@pytest.mark.django_db
def test_update_profile_multiple_fields():
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

    response = client.put(
        UPDATE_PROFILE_URL,
        {
            "full_name": "John Doe",
            "phone_number": "0987654321",
            "bank_name": "Techcombank",
            "bank_account_number": "987654321",
            "bank_account_holder": "John Doe",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == "John Doe"
    assert data["phone_number"] == "0987654321"
    assert data["bank_name"] == "Techcombank"
    assert data["bank_account_number"] == "987654321"
    assert data["bank_account_holder"] == "John Doe"

    user.refresh_from_db()
    assert user.full_name == "John Doe"
    assert user.phone_number == "0987654321"
    assert user.bank_name == "Techcombank"
    assert user.bank_account_number == "987654321"
    assert user.bank_account_holder == "John Doe"
