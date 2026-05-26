import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember
from expenses.models import Expense, ExpenseParticipant


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_update_expense_url(expense_id):
    return f"/api/expenses/{expense_id}/"


@pytest.mark.django_db
def test_update_expense_success():
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

    expense = Expense.objects.create(
        household=household,
        title="Dinner",
        amount=100000,
        payer=payer,
        split_type="equal",
    )

    ExpenseParticipant.objects.create(
        expense=expense,
        user=payer,
        share_amount=50000,
    )

    ExpenseParticipant.objects.create(
        expense=expense,
        user=participant,
        share_amount=50000,
    )

    token = get_auth_header(payer)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.put(
        get_update_expense_url(expense.id),
        {
            "title": "Updated Dinner",
            "amount": 120000,
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

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Dinner"
    assert Decimal(str(data["amount"])) == Decimal("120000")

    expense.refresh_from_db()
    assert expense.title == "Updated Dinner"
    assert expense.amount == 120000


@pytest.mark.django_db
def test_update_expense_not_manager():
    client = APIClient()
    user_model = get_user_model()

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
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
        owner=payer,
    )

    HouseholdMember.objects.create(
        household=household,
        user=payer,
        role=HouseholdMember.Role.OWNER,
    )

    HouseholdMember.objects.create(
        household=household,
        user=member,
        role=HouseholdMember.Role.MEMBER,
    )

    expense = Expense.objects.create(
        household=household,
        title="Dinner",
        amount=100000,
        payer=payer,
        split_type="equal",
    )

    ExpenseParticipant.objects.create(
        expense=expense,
        user=payer,
        share_amount=50000,
    )

    ExpenseParticipant.objects.create(
        expense=expense,
        user=member,
        share_amount=50000,
    )

    token = get_auth_header(member)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.put(
        get_update_expense_url(expense.id),
        {
            "title": "Updated Dinner",
            "amount": 120000,
            "payer": payer.id,
            "split_type": "equal",
            "participants": [
                {
                    "user_id": payer.id,
                },
                {
                    "user_id": member.id,
                },
            ],
        },
        format="json",
    )

    assert response.status_code == 400

    data = response.json()
    assert "detail" in data or "non_field_errors" in data


@pytest.mark.django_db
def test_update_expense_not_found():
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

    import uuid
    fake_id = uuid.uuid4()

    response = client.put(
        get_update_expense_url(fake_id),
        {
            "title": "Updated",
            "amount": 100000,
            "split_type": "equal",
            "participants": [
                {
                    "user_id": user.id,
                },
            ],
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_update_expense_unauthenticated():
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

    expense = Expense.objects.create(
        household=household,
        title="Dinner",
        amount=100000,
        payer=payer,
        split_type="equal",
    )

    response = client.put(
        get_update_expense_url(expense.id),
        {
            "title": "Updated",
            "amount": 120000,
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
def test_update_expense_invalid_amount():
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

    expense = Expense.objects.create(
        household=household,
        title="Dinner",
        amount=100000,
        payer=payer,
        split_type="equal",
    )

    ExpenseParticipant.objects.create(
        expense=expense,
        user=payer,
        share_amount=100000,
    )

    token = get_auth_header(payer)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.put(
        get_update_expense_url(expense.id),
        {
            "title": "Updated",
            "amount": 0,
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
