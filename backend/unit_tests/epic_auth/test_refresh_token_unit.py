import unittest

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class TestRefreshTokenUnit(unittest.TestCase):
    """Unit tests for refresh token serializer validation."""

    def test_refresh_token_missing_field(self):
        """Return error when refresh field is missing."""
        serializer = TokenRefreshSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("refresh", serializer.errors)

    def test_refresh_token_invalid_value(self):
        """Raise TokenError for malformed refresh token value."""
        serializer = TokenRefreshSerializer(data={"refresh": "invalid"})
        with self.assertRaises(TokenError):
            serializer.is_valid(raise_exception=True)


if __name__ == "__main__":
    unittest.main()
