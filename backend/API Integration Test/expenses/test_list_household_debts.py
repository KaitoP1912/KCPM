import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember
from expenses.models import Expense, ExpenseParticipant, Debt


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_list_debts_url(household_id):
    return f"/api/expenses/household/{household_id}/debts/"


@pytest.mark.django_db
def test_list_household_debts_success():
    client = APIClient()
    user_model = get_user_model()

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    debtor = user_model.objects.create_user(
        email="debtor@example.com",
        username="debtor",
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
        user=debtor,
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
        user=debtor,
        share_amount=50000,
    )

    Debt.objects.create(
        household=household,
        expense=expense,
        from_user=debtor,
        to_user=payer,
        amount=50000,
        is_paid=False,
    )

    token = get_auth_header(debtor)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_list_debts_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert len(data["results"]) >= 1
    assert Decimal(str(data["results"][0]["amount"])) == Decimal("50000")


@pytest.mark.django_db
def test_list_household_debts_empty():
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
        get_list_debts_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


@pytest.mark.django_db
def test_list_household_debts_not_member():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
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
        owner=owner,
    )

    HouseholdMember.objects.create(
        household=household,
        user=owner,
        role=HouseholdMember.Role.OWNER,
    )

    token = get_auth_header(non_member)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_list_debts_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


@pytest.mark.django_db
def test_list_household_debts_unauthenticated():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    household = Household.objects.create(
        name="Test Household",
        owner=owner,
    )

    response = client.get(
        get_list_debts_url(household.id),
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_household_debts_paid_excluded():
    client = APIClient()
    user_model = get_user_model()

    payer = user_model.objects.create_user(
        email="payer@example.com",
        username="payer",
        password="StrongPass123",
        email_verified=True,
        is_active=True,
    )

    debtor = user_model.objects.create_user(
        email="debtor@example.com",
        username="debtor",
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
        user=debtor,
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
        user=debtor,
        share_amount=50000,
    )

    Debt.objects.create(
        household=household,
        expense=expense,
        from_user=debtor,
        to_user=payer,
        amount=50000,
        is_paid=True,
    )

    token = get_auth_header(debtor)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_list_debts_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0
