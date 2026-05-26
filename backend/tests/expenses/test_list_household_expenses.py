import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from households.models import Household, HouseholdMember
from expenses.models import Expense, ExpenseParticipant


def get_auth_header(user):
    refresh = RefreshToken.for_user(user)
    return f'Bearer {str(refresh.access_token)}'


def get_list_expenses_url(household_id):
    return f"/api/expenses/household/{household_id}/"


@pytest.mark.django_db
def test_list_household_expenses_success():
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

    expense1 = Expense.objects.create(
        household=household,
        title="Dinner",
        amount=100000,
        payer=payer,
        split_type="equal",
    )

    ExpenseParticipant.objects.create(
        expense=expense1,
        user=payer,
        share_amount=100000,
    )

    expense2 = Expense.objects.create(
        household=household,
        title="Lunch",
        amount=50000,
        payer=payer,
        split_type="equal",
    )

    ExpenseParticipant.objects.create(
        expense=expense2,
        user=payer,
        share_amount=50000,
    )

    token = get_auth_header(payer)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_list_expenses_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert len(data["results"]) == 2


@pytest.mark.django_db
def test_list_household_expenses_empty():
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

    response = client.get(
        get_list_expenses_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert len(data["results"]) == 0


@pytest.mark.django_db
def test_list_household_expenses_not_member():
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

    expense = Expense.objects.create(
        household=household,
        title="Dinner",
        amount=100000,
        payer=owner,
        split_type="equal",
    )

    ExpenseParticipant.objects.create(
        expense=expense,
        user=owner,
        share_amount=100000,
    )

    token = get_auth_header(non_member)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_list_expenses_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


@pytest.mark.django_db
def test_list_household_expenses_unauthenticated():
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
        get_list_expenses_url(household.id),
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_household_expenses_pagination():
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

    for i in range(25):
        expense = Expense.objects.create(
            household=household,
            title=f"Expense {i}",
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

    response = client.get(
        get_list_expenses_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert "count" in data
    assert data["count"] == 25
    assert len(data["results"]) <= 20


@pytest.mark.django_db
def test_list_household_expenses_as_member():
    client = APIClient()
    user_model = get_user_model()

    owner = user_model.objects.create_user(
        email="owner@example.com",
        username="owner",
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
        owner=owner,
    )

    HouseholdMember.objects.create(
        household=household,
        user=owner,
        role=HouseholdMember.Role.OWNER,
    )

    HouseholdMember.objects.create(
        household=household,
        user=member,
        role=HouseholdMember.Role.MEMBER,
    )

    expense1 = Expense.objects.create(
        household=household,
        title="Owner Expense",
        amount=100000,
        payer=owner,
        split_type="equal",
    )

    ExpenseParticipant.objects.create(
        expense=expense1,
        user=owner,
        share_amount=50000,
    )

    ExpenseParticipant.objects.create(
        expense=expense1,
        user=member,
        share_amount=50000,
    )

    expense2 = Expense.objects.create(
        household=household,
        title="Member Expense",
        amount=80000,
        payer=member,
        split_type="equal",
    )

    ExpenseParticipant.objects.create(
        expense=expense2,
        user=member,
        share_amount=80000,
    )

    token = get_auth_header(member)
    client.credentials(HTTP_AUTHORIZATION=token)

    response = client.get(
        get_list_expenses_url(household.id),
        format="json",
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
