import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from households.models import Household, HouseholdMember
from expenses.models import Expense, ExpenseParticipant


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_expense_detail_url(expense_id):
    return f"/api/expenses/{expense_id}/"


@pytest.mark.django_db
def test_get_expense_detail_success():
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
        note="Shared dinner",
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

    response = client.get(
        get_expense_detail_url(expense.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(expense.id)
    assert data["title"] == "Dinner"
    assert Decimal(str(data["amount"])) == Decimal("100000")
    assert data["note"] == "Shared dinner"
    assert "participants" in data
    assert len(data["participants"]) == 2


@pytest.mark.django_db
def test_get_expense_detail_not_found():
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

    response = client.get(
        get_expense_detail_url(fake_id),
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_get_expense_detail_unauthenticated():
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

    response = client.get(
        get_expense_detail_url(expense.id),
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_expense_detail_not_member():
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

    token = get_auth_header(non_member)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_expense_detail_url(expense.id),
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_get_expense_detail_as_member():
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

    response = client.get(
        get_expense_detail_url(expense.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(expense.id)
    assert "participants" in data
