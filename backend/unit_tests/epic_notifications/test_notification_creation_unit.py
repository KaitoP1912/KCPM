import unittest
from types import SimpleNamespace
from unittest.mock import patch

from notifications.services import create_notification


class TestNotificationCreationUnit(unittest.TestCase):
    """Unit tests for notification creation helper."""

    def test_create_notification_returns_notification(self):
        notification = SimpleNamespace(id="id", notification_type="type")

        with patch("notifications.services.Notification") as model, patch(
            "notifications.services.send_push_notification_to_user"
        ) as send_push:
            model.objects.create.return_value = notification

            result = create_notification(
                recipient=SimpleNamespace(email="user@example.com"),
                actor=SimpleNamespace(email="actor@example.com"),
                notification_type="type",
                title="Title",
            )

        self.assertEqual(result, notification)
        send_push.assert_called_once()

    def test_create_notification_handles_push_failure(self):
        notification = SimpleNamespace(id="id", notification_type="type")

        with patch("notifications.services.Notification") as model, patch(
            "notifications.services.send_push_notification_to_user",
            side_effect=Exception("push failed"),
        ):
            model.objects.create.return_value = notification

            result = create_notification(
                recipient=SimpleNamespace(email="user@example.com"),
                actor=SimpleNamespace(email="actor@example.com"),
                notification_type="type",
                title="Title",
            )

        self.assertEqual(result, notification)


if __name__ == "__main__":
    unittest.main()
