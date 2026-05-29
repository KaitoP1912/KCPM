import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from households.serializers import (
    VIRTUAL_MEMBER_EMAIL_DOMAIN,
    get_user_display_name,
    is_virtual_user,
)
from households.views import AddHouseholdMemberView

pytestmark = pytest.mark.django_db


class TestAddMemberUnit(unittest.TestCase):
    """Unit tests for household member display helpers."""

    def test_virtual_user_detection(self):
        """Detect virtual members by email domain."""
        user = SimpleNamespace(email=f"a{VIRTUAL_MEMBER_EMAIL_DOMAIN}")

        self.assertTrue(is_virtual_user(user))

    def test_virtual_user_display_name_default(self):
        """Fallback to default name for virtual users with empty full_name."""
        user = SimpleNamespace(email=f"a{VIRTUAL_MEMBER_EMAIL_DOMAIN}", full_name="")

        self.assertEqual(get_user_display_name(user), "Thành viên ảo")

    def test_normal_user_display_name_prefers_full_name(self):
        """Prefer full_name when provided for normal users."""
        user = SimpleNamespace(email="user@example.com", full_name="User Name")

        self.assertEqual(get_user_display_name(user), "User Name")

    def test_add_member_returns_403_when_not_member(self):
        """Reject add-member when requester is not in household."""
        request = SimpleNamespace(
            data={"email": "new@example.com"},
            user=SimpleNamespace(id=1),
        )

        with patch("households.views.Household") as household_model:
            household_model.objects.select_for_update.return_value.filter.return_value.first.return_value = None
            response = AddHouseholdMemberView().post(request, household_id="id")

        self.assertEqual(response.status_code, 403)

    def test_add_member_returns_403_when_not_owner(self):
        """Reject add-member when requester is not an owner."""
        request = SimpleNamespace(
            data={"email": "new@example.com"},
            user=SimpleNamespace(id=1),
        )
        household = SimpleNamespace(id="id")

        with patch("households.views.Household") as household_model, patch(
            "households.views.HouseholdMember"
        ) as member_model:
            household_model.objects.select_for_update.return_value.filter.return_value.first.return_value = household
            member_model.objects.filter.return_value.first.return_value = None
            response = AddHouseholdMemberView().post(request, household_id="id")

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
