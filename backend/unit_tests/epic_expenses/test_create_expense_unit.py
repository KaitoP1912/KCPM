import unittest
from decimal import Decimal
from types import SimpleNamespace

from rest_framework import serializers

from expenses.models import Expense
from expenses.serializers import ExpenseCreateUpdateSerializer


class TestCreateExpenseUnit(unittest.TestCase):
    """Unit tests for expense creation validation and split logic."""

    def test_validate_title_rejects_blank(self):
        serializer = ExpenseCreateUpdateSerializer()

        with self.assertRaises(serializers.ValidationError):
            serializer.validate_title("   ")

    def test_validate_amount_rejects_non_positive(self):
        serializer = ExpenseCreateUpdateSerializer()

        with self.assertRaises(serializers.ValidationError):
            serializer.validate_amount(Decimal("0"))

    def test_build_split_items_equal(self):
        serializer = ExpenseCreateUpdateSerializer()
        users_by_id = {
            1: SimpleNamespace(id=1),
            2: SimpleNamespace(id=2),
            3: SimpleNamespace(id=3),
        }

        participants = [
            {"user_id": 1},
            {"user_id": 2},
            {"user_id": 3},
        ]

        split_items = serializer._build_split_items(
            amount=Decimal("100"),
            split_type=Expense.SplitType.EQUAL,
            participants=participants,
            users_by_id=users_by_id,
        )

        shares = [item[1] for item in split_items]
        self.assertEqual(shares, [Decimal("34"), Decimal("33"), Decimal("33")])

    def test_build_split_items_manual_requires_share_amount(self):
        serializer = ExpenseCreateUpdateSerializer()
        users_by_id = {1: SimpleNamespace(id=1)}

        with self.assertRaises(serializers.ValidationError):
            serializer._build_split_items(
                amount=Decimal("100"),
                split_type=Expense.SplitType.MANUAL,
                participants=[{"user_id": 1}],
                users_by_id=users_by_id,
            )

    def test_build_split_items_manual_total_mismatch(self):
        serializer = ExpenseCreateUpdateSerializer()
        users_by_id = {
            1: SimpleNamespace(id=1),
            2: SimpleNamespace(id=2),
        }

        with self.assertRaises(serializers.ValidationError):
            serializer._build_split_items(
                amount=Decimal("100"),
                split_type=Expense.SplitType.MANUAL,
                participants=[
                    {"user_id": 1, "share_amount": Decimal("40")},
                    {"user_id": 2, "share_amount": Decimal("40")},
                ],
                users_by_id=users_by_id,
            )


if __name__ == "__main__":
    unittest.main()
