import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember
from expenses.models import Expense, ExpenseParticipant


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_delete_expense_url(expense_id):
    return f"/api/expenses/{expense_id}/"


@pytest.mark.django_db
def test_delete_expense_success():
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

    response = client.delete(
        get_delete_expense_url(expense.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    expense_exists = Expense.objects.filter(
        id=expense.id,
    ).exists()
    assert expense_exists is False


@pytest.mark.django_db
def test_delete_expense_not_manager():
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

    response = client.delete(
        get_delete_expense_url(expense.id),
        format="json",
    )

    assert response.status_code == 403

    data = response.json()
    assert "detail" in data


@pytest.mark.django_db
def test_delete_expense_not_found():
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

    response = client.delete(
        get_delete_expense_url(fake_id),
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_expense_unauthenticated():
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

    response = client.delete(
        get_delete_expense_url(expense.id),
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_delete_expense_by_owner():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
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
        user=payer,
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
        share_amount=100000,
    )

    token = get_auth_header(owner)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.delete(
        get_delete_expense_url(expense.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    expense_exists = Expense.objects.filter(
        id=expense.id,
    ).exists()
    assert expense_exists is False
