from django.urls import path

from households.views import (
    ActivityListView,
    AddHouseholdMemberView,
    AllActivityListView,
    HouseholdDetailView,
    HouseholdListCreateView,
    HouseholdSummaryListView,
    JoinHouseholdView,
    KickHouseholdMemberView,
    LeaveHouseholdView,
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
        'summary/',
        HouseholdSummaryListView.as_view(),
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
        '<uuid:household_id>/members/<uuid:member_id>/kick/',
        KickHouseholdMemberView.as_view(),
    ),

    path(
        '<uuid:household_id>/leave/',
        LeaveHouseholdView.as_view(),
    ),

    path(
        '<uuid:household_id>/activities/',
        ActivityListView.as_view(),
    ),
]