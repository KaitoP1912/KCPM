import unittest

from households.serializers import JoinHouseholdSerializer


class TestJoinByInviteCodeUnit(unittest.TestCase):
    """Unit tests for invite code normalization."""

    def test_join_by_invite_code_normalizes(self):
        serializer = JoinHouseholdSerializer()

        value = serializer.validate_invite_code("  abcd1234 ")

        self.assertEqual(value, "ABCD1234")


if __name__ == "__main__":
    unittest.main()
