import unittest
from types import SimpleNamespace

from notifications.serializers import NotificationSerializer


class TestListNotificationsUnit(unittest.TestCase):
    """Unit tests for notification serializer display fields."""

    def test_actor_name_prefers_full_name(self):
        actor = SimpleNamespace(full_name="Actor", email="actor@example.com")
        notification = SimpleNamespace(actor=actor, household=None)

        name = NotificationSerializer().get_actor_name(notification)

        self.assertEqual(name, "Actor")

    def test_actor_name_falls_back_to_email(self):
        actor = SimpleNamespace(full_name="", email="actor@example.com")
        notification = SimpleNamespace(actor=actor, household=None)

        name = NotificationSerializer().get_actor_name(notification)

        self.assertEqual(name, "actor@example.com")

    def test_household_name_none_when_missing(self):
        """Return None when notification has no household."""
        notification = SimpleNamespace(household=None)

        self.assertIsNone(NotificationSerializer().get_household_name(notification))

    def test_notification_serializer_includes_recipient(self):
        """Ensure response contract includes recipient field."""
        serializer = NotificationSerializer()

        self.assertIn("recipient", serializer.fields)


if __name__ == "__main__":
    unittest.main()
