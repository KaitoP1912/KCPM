from django.urls import path

from households.views import (
    ActivityListView,
    AllActivityListView,
    HouseholdDetailView,
    HouseholdListCreateView,
    JoinHouseholdView,
)

urlpatterns = [
    path(
        '',
        HouseholdListCreateView.as_view(),
    ),

    path(
        'join/',
        JoinHouseholdView.as_view(),
    ),

    path(
        'activities/',
        AllActivityListView.as_view(),
    ),

    path(
        '<uuid:pk>/',
        HouseholdDetailView.as_view(),
    ),

    path(
        '<uuid:household_id>/activities/',
        ActivityListView.as_view(),
    ),
]