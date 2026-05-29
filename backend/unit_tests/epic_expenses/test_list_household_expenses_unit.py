import unittest
from types import SimpleNamespace
from unittest.mock import patch

from expenses.serializers import ExpenseListSerializer


class FakeRequest:
    def build_absolute_uri(self, value):
        return f"https://example.com/{value}"


class TestListHouseholdExpensesUnit(unittest.TestCase):
    """Unit tests for expense list serializer helpers."""

    def test_get_payer_name_uses_display_helper(self):
        serializer = ExpenseListSerializer()
        expense = SimpleNamespace(payer=SimpleNamespace())

        with patch("expenses.serializers.get_user_display_name", return_value="Name"):
            name = serializer.get_payer_name(expense)

        self.assertEqual(name, "Name")

    def test_get_payer_avatar_empty_when_no_request(self):
        serializer = ExpenseListSerializer()
        expense = SimpleNamespace(payer=SimpleNamespace(avatar=None))

        self.assertEqual(serializer.get_payer_avatar(expense), "")

    def test_get_payer_avatar_with_request(self):
        request = FakeRequest()
        serializer = ExpenseListSerializer(context={"request": request})
        expense = SimpleNamespace(payer=SimpleNamespace(avatar=SimpleNamespace(url="avatar.png")))

        avatar_url = serializer.get_payer_avatar(expense)

        self.assertTrue(avatar_url.endswith("avatar.png"))


if __name__ == "__main__":
    unittest.main()
