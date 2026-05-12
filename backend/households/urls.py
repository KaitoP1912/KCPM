from django.urls import path

from households.views import (
    HouseholdListCreateView,
    HouseholdDetailView,
    AddHouseholdMemberView,
)


urlpatterns = [
    path('', HouseholdListCreateView.as_view()),
    path('<uuid:pk>/', HouseholdDetailView.as_view()),
    path('<uuid:pk>/members/add/', AddHouseholdMemberView.as_view()),
]