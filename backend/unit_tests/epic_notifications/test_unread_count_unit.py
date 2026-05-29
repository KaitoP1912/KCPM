import unittest
from types import SimpleNamespace
from unittest.mock import patch

from notifications.views import NotificationUnreadCountView


class TestUnreadCountUnit(unittest.TestCase):
    """Unit tests for unread count endpoint logic."""

    def test_unread_count_only_unread(self):
        request = SimpleNamespace(user=SimpleNamespace(id=1))

        with patch("notifications.views.Notification") as model:
            model.objects.filter.return_value.count.return_value = 5
            response = NotificationUnreadCountView().get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["unread_count"], 5)


if __name__ == "__main__":
    unittest.main()
