import unittest
from types import SimpleNamespace
from unittest.mock import patch

from expenses.serializers import is_household_owner


class TestDeleteExpenseUnit(unittest.TestCase):
    """Unit tests for household owner checks."""

    def test_is_household_owner_true(self):
        user = SimpleNamespace(id=1)
        household = SimpleNamespace(id=2)

        with patch("expenses.serializers.HouseholdMember") as member_model:
            member_model.objects.filter.return_value.exists.return_value = True
            result = is_household_owner(user, household)

        self.assertTrue(result)

    def test_is_household_owner_false(self):
        user = SimpleNamespace(id=1)
        household = SimpleNamespace(id=2)

        with patch("expenses.serializers.HouseholdMember") as member_model:
            member_model.objects.filter.return_value.exists.return_value = False
            result = is_household_owner(user, household)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
