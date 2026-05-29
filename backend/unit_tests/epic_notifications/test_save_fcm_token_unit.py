import unittest
from types import SimpleNamespace
from unittest.mock import patch

from notifications.models import FCMDevice
from notifications.views import SaveFCMTokenView


class TestSaveFcmTokenUnit(unittest.TestCase):
    """Unit tests for saving FCM token."""

    def test_save_fcm_token_missing_token(self):
        request = SimpleNamespace(data={}, user=SimpleNamespace(id=1))

        response = SaveFCMTokenView().post(request)

        self.assertEqual(response.status_code, 400)

    def test_save_fcm_token_default_device_type(self):
        request = SimpleNamespace(
            data={"token": "token123"},
            user=SimpleNamespace(id=1),
        )

        with patch("notifications.views.FCMDevice") as model:
            response = SaveFCMTokenView().post(request)

        self.assertEqual(response.status_code, 200)
        model.objects.update_or_create.assert_called_once()

    def test_save_fcm_token_custom_device_type(self):
        request = SimpleNamespace(
            data={"token": "token123", "device_type": FCMDevice.DeviceType.IOS},
            user=SimpleNamespace(id=1),
        )

        with patch("notifications.views.FCMDevice") as model:
            response = SaveFCMTokenView().post(request)

        self.assertEqual(response.status_code, 200)
        model.objects.update_or_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
