from django.urls import path

from households.views import (
    ActivityListView,
    AddHouseholdMemberView,
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
        '<uuid:household_id>/members/add/',
        AddHouseholdMemberView.as_view(),
    ),

    path(
        '<uuid:household_id>/activities/',
        ActivityListView.as_view(),
    ),
]
