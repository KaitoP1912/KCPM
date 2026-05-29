import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from accounts.serializers import ChangePasswordSerializer
from accounts.views import ChangePasswordView


class TestChangePasswordUnit(unittest.TestCase):
    """Unit tests for change password validation and view logic."""

    def test_change_password_confirm_mismatch(self):
        """Reject when new password and confirm do not match."""
        serializer = ChangePasswordSerializer(
            data={
                "old_password": "OldPass123",
                "new_password": "NewPass123",
                "confirm_password": "Mismatch",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("confirm_password", serializer.errors)

    def test_change_password_wrong_old_password(self):
        """Return 400 when old password does not match."""
        request = SimpleNamespace(
            data={
                "old_password": "WrongOld",
                "new_password": "NewPass123",
                "confirm_password": "NewPass123",
            },
            user=SimpleNamespace(password="hashed"),
        )

        with patch("accounts.views.check_password", return_value=False):
            response = ChangePasswordView().post(request)

        self.assertEqual(response.status_code, 400)

    def test_change_password_success(self):
        """Update password when old password is valid."""
        user = SimpleNamespace(
            password="hashed",
            set_password=MagicMock(),
            save=MagicMock(),
        )

        request = SimpleNamespace(
            data={
                "old_password": "OldPass123",
                "new_password": "NewPass123",
                "confirm_password": "NewPass123",
            },
            user=user,
        )

        with patch("accounts.views.check_password", return_value=True):
            response = ChangePasswordView().post(request)

        self.assertEqual(response.status_code, 200)
        user.set_password.assert_called_once_with("NewPass123")
        user.save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
