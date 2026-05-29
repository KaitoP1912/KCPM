import unittest
from types import SimpleNamespace

from households.views import money_to_int, serialize_debt_user


class FakeRequest:
    def build_absolute_uri(self, value):
        return f"https://example.com/{value}"


class TestKickMemberUnit(unittest.TestCase):
    """Unit tests for household helper utilities."""

    def test_money_to_int_handles_none(self):
        self.assertEqual(money_to_int(None), 0)

    def test_serialize_debt_user_includes_avatar_url(self):
        user = SimpleNamespace(
            id=1,
            email="user@example.com",
            full_name="User",
            avatar=SimpleNamespace(url="avatar.png"),
        )

        data = serialize_debt_user(user, request=FakeRequest())

        self.assertEqual(data["other_user_id"], 1)
        self.assertEqual(data["other_name"], "User")
        self.assertTrue(data["other_avatar"].endswith("avatar.png"))


if __name__ == "__main__":
    unittest.main()
