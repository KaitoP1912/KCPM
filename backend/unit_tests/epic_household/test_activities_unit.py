import unittest
from types import SimpleNamespace
from unittest.mock import patch

from households.serializers import (
    ActivitySerializer,
    VIRTUAL_MEMBER_EMAIL_DOMAIN,
)
from households.views import ActivityListView


class TestActivitiesUnit(unittest.TestCase):
    """Unit tests for activity serializer display logic."""

    def test_activity_actor_name_virtual_user(self):
        """Show virtual member display name for activities."""
        actor = SimpleNamespace(
            email=f"actor{VIRTUAL_MEMBER_EMAIL_DOMAIN}",
            full_name="",
        )
        activity = SimpleNamespace(actor=actor)

        name = ActivitySerializer().get_actor_name(activity)

        self.assertEqual(name, "Thành viên ảo")

    def test_activity_actor_name_normal_user(self):
        """Show full name for normal users in activity feed."""
        actor = SimpleNamespace(
            email="actor@example.com",
            full_name="Actor Name",
        )
        activity = SimpleNamespace(actor=actor)

        name = ActivitySerializer().get_actor_name(activity)

        self.assertEqual(name, "Actor Name")

    def test_activity_list_filters_by_membership(self):
        """Filter activities by household and requesting member."""
        view = ActivityListView()
        view.kwargs = {"household_id": "id"}
        view.request = SimpleNamespace(user=SimpleNamespace(id=1))

        with patch("households.views.Activity") as activity_model:
            activity_model.objects.filter.return_value.select_related.return_value.order_by.return_value = []
            view.get_queryset()

        activity_model.objects.filter.assert_called_once_with(
            household_id="id",
            household__members__user=view.request.user,
        )


if __name__ == "__main__":
    unittest.main()
