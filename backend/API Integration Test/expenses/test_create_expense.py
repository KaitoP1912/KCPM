import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember
from expenses.models import Expense


CREATE_EXPENSE_URL = "/api/expenses/"


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


@pytest.mark.django_db
def test_create_expense_success():
    client = APIClient()
    user_model = get_user_model()

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    participant = user_model.objects.create_user(
        email="participant@example.com",
        username="participant",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=payer,
    )

    HouseholdMember.objects.create(
        household=household,
        user=payer,
        role=HouseholdMember.Role.OWNER,
    )

    HouseholdMember.objects.create(
        household=household,
        user=participant,
        role=HouseholdMember.Role.MEMBER,
    )

    token = get_auth_header(payer)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        CREATE_EXPENSE_URL,
        {
            "household": household.id,
            "title": "Dinner",
            "amount": 100000,
            "payer": payer.id,
            "split_type": "equal",
            "participants": [
                {
                    "user_id": payer.id,
                },
                {
                    "user_id": participant.id,
                },
            ],
        },
        format="json",
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["title"] == "Dinner"
    assert Decimal(str(data["amount"])) == Decimal("100000")
    assert data["household"] == str(household.id)

    expense = Expense.objects.get(id=data["id"])
    assert expense.payer == payer
    assert expense.split_type == "equal"


@pytest.mark.django_db
def test_create_expense_missing_title():
    client = APIClient()
    user_model = get_user_model()

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=payer,
    )

    HouseholdMember.objects.create(
        household=household,
        user=payer,
        role=HouseholdMember.Role.OWNER,
    )

    token = get_auth_header(payer)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        CREATE_EXPENSE_URL,
        {
            "household": household.id,
            "amount": 100000,
            "payer": payer.id,
            "split_type": "equal",
            "participants": [
                {
                    "user_id": payer.id,
                },
            ],
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "title" in data


@pytest.mark.django_db
def test_create_expense_invalid_amount():
    client = APIClient()
    user_model = get_user_model()

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=payer,
    )

    HouseholdMember.objects.create(
        household=household,
        user=payer,
        role=HouseholdMember.Role.OWNER,
    )

    token = get_auth_header(payer)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        CREATE_EXPENSE_URL,
        {
            "household": household.id,
            "title": "Dinner",
            "amount": -100,
            "payer": payer.id,
            "split_type": "equal",
            "participants": [
                {
                    "user_id": payer.id,
                },
            ],
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "amount" in data


@pytest.mark.django_db
def test_create_expense_not_member():
    client = APIClient()
    user_model = get_user_model()

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    non_member = user_model.objects.create_user(
        email="nonmember@example.com",
        username="nonmember",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=payer,
    )

    HouseholdMember.objects.create(
        household=household,
        user=payer,
        role=HouseholdMember.Role.OWNER,
    )

    token = get_auth_header(non_member)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        CREATE_EXPENSE_URL,
        {
            "household": household.id,
            "title": "Dinner",
            "amount": 100000,
            "payer": payer.id,
            "split_type": "equal",
            "participants": [
                {
                    "user_id": payer.id,
                },
            ],
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data or "non_field_errors" in data


@pytest.mark.django_db
def test_create_expense_unauthenticated():
    client = APIClient()
    user_model = get_user_model()

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=payer,
    )

    response = client.post(
        CREATE_EXPENSE_URL,
        {
            "household": household.id,
            "title": "Dinner",
            "amount": 100000,
            "payer": payer.id,
            "split_type": "equal",
            "participants": [
                {
                    "user_id": payer.id,
                },
            ],
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_expense_empty_participants():
    client = APIClient()
    user_model = get_user_model()

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=payer,
    )

    HouseholdMember.objects.create(
        household=household,
        user=payer,
        role=HouseholdMember.Role.OWNER,
    )

    token = get_auth_header(payer)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.post(
        CREATE_EXPENSE_URL,
        {
            "household": household.id,
            "title": "Dinner",
            "amount": 100000,
            "payer": payer.id,
            "split_type": "equal",
            "participants": [],
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "participants" in data or "non_field_errors" in data
