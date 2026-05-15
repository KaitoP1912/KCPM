from django.urls import path

from households.views import (
    ActivityListView,
    AddHouseholdMemberView,
    AllActivityListView,
    HouseholdDetailView,
    HouseholdListCreateView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationUnreadCountView,
)


urlpatterns = [
    path('', HouseholdListCreateView.as_view()),
    path('activities/', AllActivityListView.as_view()),
    path('notifications/', NotificationListView.as_view()),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view()),
    path('notifications/mark-all-read/', NotificationMarkAllReadView.as_view()),
    path('notifications/<uuid:pk>/read/', NotificationMarkReadView.as_view()),
    path('<uuid:pk>/', HouseholdDetailView.as_view()),
    path('<uuid:pk>/members/add/', AddHouseholdMemberView.as_view()),
    path('<uuid:household_id>/activities/', ActivityListView.as_view()),
]