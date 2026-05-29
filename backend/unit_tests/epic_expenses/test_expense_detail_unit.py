import unittest
from types import SimpleNamespace
from unittest.mock import patch

from expenses.serializers import (
    ExpenseListSerializer,
    VIRTUAL_MEMBER_EMAIL_DOMAIN,
    format_money,
    get_user_display_name,
)


class TestExpenseDetailUnit(unittest.TestCase):
    """Unit tests for expense detail display helpers."""

    def test_format_money_formats_with_dot_separator(self):
        self.assertEqual(format_money(123456), "123.456đ")

    def test_get_user_display_name_virtual_user(self):
        user = SimpleNamespace(email=f"u{VIRTUAL_MEMBER_EMAIL_DOMAIN}", full_name="")

        self.assertEqual(get_user_display_name(user), "Thành viên ảo")

    def test_can_manage_false_without_request(self):
        serializer = ExpenseListSerializer()

        self.assertFalse(serializer.get_can_manage(SimpleNamespace()))

    def test_can_manage_uses_permission_helper(self):
        request = SimpleNamespace(user=SimpleNamespace(id=1))
        serializer = ExpenseListSerializer(context={"request": request})
        expense = SimpleNamespace()

        with patch("expenses.serializers.is_user_expense_manager", return_value=True):
            result = serializer.get_can_manage(expense)

        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
