import unittest
from types import SimpleNamespace
from unittest.mock import patch

from expenses.serializers import is_user_expense_manager


class TestUpdateExpenseUnit(unittest.TestCase):
    """Unit tests for expense manager permission helper."""

    def test_is_user_expense_manager_true_for_payer(self):
        user = SimpleNamespace(id=1)
        expense = SimpleNamespace(payer_id=1, household="h")

        self.assertTrue(is_user_expense_manager(user, expense))

    def test_is_user_expense_manager_uses_household_owner(self):
        user = SimpleNamespace(id=2)
        expense = SimpleNamespace(payer_id=1, household="h")

        with patch("expenses.serializers.is_household_owner", return_value=True) as is_owner:
            result = is_user_expense_manager(user, expense)

        self.assertTrue(result)
        is_owner.assert_called_once_with(user, "h")

    def test_is_user_expense_manager_false_when_not_owner_or_payer(self):
        user = SimpleNamespace(id=2)
        expense = SimpleNamespace(payer_id=1, household="h")

        with patch("expenses.serializers.is_household_owner", return_value=False):
            result = is_user_expense_manager(user, expense)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
