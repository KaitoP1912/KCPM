import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from households.views import (
    get_owner_household_or_response,
    get_virtual_user_or_response,
    VIRTUAL_MEMBER_EMAIL_DOMAIN,
)


class TestLeaveHouseholdUnit(unittest.TestCase):
    """Unit tests for ownership and virtual member helpers."""

    def test_get_owner_household_returns_404_when_not_member(self):
        request = SimpleNamespace(user=SimpleNamespace(id=1))

        with patch("households.views.Household") as household_model:
            household_model.objects.filter.return_value.distinct.return_value.first.return_value = None
            household, response = get_owner_household_or_response(request, "id")

        self.assertIsNone(household)
        self.assertEqual(response.status_code, 404)

    def test_get_owner_household_returns_403_when_not_owner(self):
        request = SimpleNamespace(user=SimpleNamespace(id=1))
        household = SimpleNamespace(id="id")

        with patch("households.views.Household") as household_model, patch("households.views.HouseholdMember") as member_model:
            household_model.objects.filter.return_value.distinct.return_value.first.return_value = household
            member_model.objects.filter.return_value.exists.return_value = False
            resolved, response = get_owner_household_or_response(request, "id")

        self.assertIsNone(resolved)
        self.assertEqual(response.status_code, 403)

    def test_get_owner_household_returns_household_for_owner(self):
        request = SimpleNamespace(user=SimpleNamespace(id=1))
        household = SimpleNamespace(id="id")

        with patch("households.views.Household") as household_model, patch("households.views.HouseholdMember") as member_model:
            household_model.objects.filter.return_value.distinct.return_value.first.return_value = household
            member_model.objects.filter.return_value.exists.return_value = True
            resolved, response = get_owner_household_or_response(request, "id")

        self.assertEqual(resolved, household)
        self.assertIsNone(response)

    def test_get_virtual_user_returns_404_when_not_member(self):
        household = SimpleNamespace(id="id")

        with patch("households.views.HouseholdMember") as member_model:
            member_model.objects.filter.return_value.select_related.return_value.first.return_value = None
            user, response = get_virtual_user_or_response(household, 1)

        self.assertIsNone(user)
        self.assertEqual(response.status_code, 404)

    def test_get_virtual_user_rejects_non_virtual(self):
        household = SimpleNamespace(id="id")
        normal_user = SimpleNamespace(email="user@example.com")
        membership = SimpleNamespace(user=normal_user)

        with patch("households.views.HouseholdMember") as member_model:
            member_model.objects.filter.return_value.select_related.return_value.first.return_value = membership
            user, response = get_virtual_user_or_response(household, 1)

        self.assertIsNone(user)
        self.assertEqual(response.status_code, 400)

    def test_get_virtual_user_returns_virtual_member(self):
        household = SimpleNamespace(id="id")
        virtual_user = SimpleNamespace(email=f"x{VIRTUAL_MEMBER_EMAIL_DOMAIN}")
        membership = SimpleNamespace(user=virtual_user)

        with patch("households.views.HouseholdMember") as member_model:
            member_model.objects.filter.return_value.select_related.return_value.first.return_value = membership
            user, response = get_virtual_user_or_response(household, 1)

        self.assertEqual(user, virtual_user)
        self.assertIsNone(response)


if __name__ == "__main__":
    unittest.main()
