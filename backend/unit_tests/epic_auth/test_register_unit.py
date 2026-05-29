import unittest
from types import SimpleNamespace
from unittest.mock import patch

from rest_framework import serializers

from accounts.serializers import RegisterSerializer


class FakeUser:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.set_password_called_with = None
        self.saved = False

    def set_password(self, value):
        self.set_password_called_with = value

    def save(self):
        self.saved = True


class TestRegisterUnit(unittest.TestCase):
    """Unit tests for RegisterSerializer business rules."""

    def test_validate_email_normalizes(self):
        """Normalize email to lowercase and trim whitespace."""
        serializer = RegisterSerializer()

        with patch("accounts.serializers.User") as user_model:
            user_model.objects.filter.return_value.first.return_value = None
            value = serializer.validate_email("  Test@Example.Com ")

        self.assertEqual(value, "test@example.com")

    def test_validate_email_rejects_verified_existing_user(self):
        """Reject registration when verified email already exists."""
        serializer = RegisterSerializer()

        existing_user = SimpleNamespace(email_verified=True)

        with patch("accounts.serializers.User") as user_model:
            user_model.objects.filter.return_value.first.return_value = existing_user
            with self.assertRaises(serializers.ValidationError):
                serializer.validate_email("test@example.com")

    def test_password_policy_min_length(self):
        """Enforce minimum password length at serializer level."""
        serializer = RegisterSerializer()

        self.assertEqual(serializer.fields["password"].min_length, 8)

    def test_create_sets_default_flags_and_hashes_password(self):
        """Set default flags and hash password on user creation."""
        serializer = RegisterSerializer()

        validated_data = {
            "email": "user@example.com",
            "username": "user",
            "password": "StrongPass123",
        }

        with patch("accounts.serializers.User", FakeUser):
            user = serializer.create(validated_data)

        self.assertFalse(user.is_active)
        self.assertFalse(user.email_verified)
        self.assertEqual(user.set_password_called_with, "StrongPass123")
        self.assertTrue(user.saved)


if __name__ == "__main__":
    unittest.main()
