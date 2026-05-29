import unittest
from types import SimpleNamespace
from unittest.mock import patch

from accounts.views import ResendRegisterOTPView


class TestResendRegistrationOtpUnit(unittest.TestCase):
    """Unit tests for ResendRegisterOTPView cooldown and resend behavior."""

    def test_resend_otp_nonexistent_user_returns_ok(self):
        """Return 200 when email does not exist to avoid account enumeration."""
        request = SimpleNamespace(data={"email": "user@example.com"})

        with patch("accounts.views.User") as user_model:
            user_model.objects.filter.return_value.first.return_value = None
            response = ResendRegisterOTPView().post(request)

        self.assertEqual(response.status_code, 200)

    def test_resend_otp_rejects_verified_user(self):
        """Return 400 when email is already verified."""
        request = SimpleNamespace(data={"email": "user@example.com"})
        user = SimpleNamespace(email_verified=True)

        with patch("accounts.views.User") as user_model:
            user_model.objects.filter.return_value.first.return_value = user
            response = ResendRegisterOTPView().post(request)

        self.assertEqual(response.status_code, 400)

    def test_resend_otp_rate_limit(self):
        """Return 429 when resend cooldown is active."""
        request = SimpleNamespace(data={"email": "user@example.com"})
        user = SimpleNamespace(email_verified=False)

        with patch("accounts.views.User") as user_model, patch("accounts.views.cache") as cache:
            user_model.objects.filter.return_value.first.return_value = user
            cache.get.return_value = True
            response = ResendRegisterOTPView().post(request)

        self.assertEqual(response.status_code, 429)

    def test_resend_otp_generates_new_otp(self):
        """Generate and send OTP when cooldown is inactive."""
        request = SimpleNamespace(data={"email": "user@example.com"})
        user = SimpleNamespace(email_verified=False)

        with patch("accounts.views.User") as user_model, patch("accounts.views.cache") as cache:
            user_model.objects.filter.return_value.first.return_value = user
            cache.get.return_value = None

            with patch("accounts.views.generate_otp", return_value="123456") as generate_otp:
                with patch("accounts.views.send_register_otp") as send_register_otp:
                    response = ResendRegisterOTPView().post(request)

        self.assertEqual(response.status_code, 200)
        generate_otp.assert_called_once()
        send_register_otp.assert_called_once_with("user@example.com", "123456")
        self.assertTrue(cache.set.called)

    def test_resend_otp_uses_lowercased_email_for_cache(self):
        """Normalize email before cache key operations."""
        request = SimpleNamespace(data={"email": "USER@EXAMPLE.COM"})
        user = SimpleNamespace(email_verified=False)

        with patch("accounts.views.User") as user_model, patch("accounts.views.cache") as cache:
            user_model.objects.filter.return_value.first.return_value = user
            cache.get.return_value = None

            with patch("accounts.views.generate_otp", return_value="123456"), patch(
                "accounts.views.send_register_otp"
            ):
                ResendRegisterOTPView().post(request)

        cache.set.assert_any_call("register_otp:user@example.com", "123456", timeout=600)
        cache.set.assert_any_call("register_otp_cooldown:user@example.com", True, timeout=60)


if __name__ == "__main__":
    unittest.main()
