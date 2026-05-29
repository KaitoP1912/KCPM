import unittest
from types import SimpleNamespace
from unittest.mock import patch

from notifications.views import NotificationMarkAllReadView


class TestMarkAllAsReadUnit(unittest.TestCase):
    """Unit tests for marking all notifications as read."""

    def test_mark_all_as_read_updates_queryset(self):
        request = SimpleNamespace(user=SimpleNamespace(id=1))

        with patch("notifications.views.Notification") as model:
            model.objects.filter.return_value.update.return_value = 3
            response = NotificationMarkAllReadView().patch(request)

        self.assertEqual(response.status_code, 200)
        model.objects.filter.assert_called_once()


if __name__ == "__main__":
    unittest.main()
