import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from notifications.views import NotificationMarkReadView


class TestMarkOneAsReadUnit(unittest.TestCase):
    """Unit tests for marking a single notification as read."""

    def test_mark_one_as_read_not_found(self):
        request = SimpleNamespace(user=SimpleNamespace(id=1))

        with patch("notifications.views.Notification") as model:
            model.objects.filter.return_value.first.return_value = None
            response = NotificationMarkReadView().patch(request, pk="id")

        self.assertEqual(response.status_code, 404)

    def test_mark_one_as_read_success(self):
        request = SimpleNamespace(user=SimpleNamespace(id=1))
        notification = SimpleNamespace(is_read=False, save=MagicMock())

        with patch("notifications.views.Notification") as model:
            model.objects.filter.return_value.first.return_value = notification
            response = NotificationMarkReadView().patch(request, pk="id")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(notification.is_read)
        notification.save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
