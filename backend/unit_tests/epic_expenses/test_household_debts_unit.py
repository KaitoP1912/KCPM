import unittest
from types import SimpleNamespace

from expenses.serializers import DebtSerializer, VIRTUAL_MEMBER_EMAIL_DOMAIN


class FakePayments:
    def filter(self, status=None):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return None


class TestHouseholdDebtsUnit(unittest.TestCase):
    """Unit tests for debt serializer helper methods."""

    def test_get_has_virtual_member_true_when_virtual(self):
        from_user = SimpleNamespace(email=f"u{VIRTUAL_MEMBER_EMAIL_DOMAIN}")
        to_user = SimpleNamespace(email="user@example.com")
        debt = SimpleNamespace(from_user=from_user, to_user=to_user)

        serializer = DebtSerializer()

        self.assertTrue(serializer.get_has_virtual_member(debt))

    def test_get_pending_payment_fields_empty_when_none(self):
        debt = SimpleNamespace(payments=FakePayments())
        serializer = DebtSerializer()

        self.assertIsNone(serializer.get_pending_payment_id(debt))
        self.assertEqual(serializer.get_pending_payment_status(debt), "")

    def test_can_mark_paid_false_without_request(self):
        debt = SimpleNamespace(is_paid=False, payments=FakePayments())
        serializer = DebtSerializer()

        self.assertFalse(serializer.get_can_mark_paid(debt))


if __name__ == "__main__":
    unittest.main()
