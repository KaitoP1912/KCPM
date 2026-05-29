import unittest

from rest_framework import serializers

from households.serializers import HouseholdSerializer


class TestCreateHouseholdUnit(unittest.TestCase):
    """Unit tests for HouseholdSerializer name validation."""

    def test_create_household_name_too_short(self):
        serializer = HouseholdSerializer()

        with self.assertRaises(serializers.ValidationError):
            serializer.validate_name("ab")

    def test_create_household_name_trims_whitespace(self):
        serializer = HouseholdSerializer()

        value = serializer.validate_name("  My Home  ")

        self.assertEqual(value, "My Home")


if __name__ == "__main__":
    unittest.main()
