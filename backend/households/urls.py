from django.urls import path

from households.views import (
    HouseholdListCreateView,
    HouseholdDetailView,
)


urlpatterns = [
    path('', HouseholdListCreateView.as_view()),
    path('<uuid:pk>/', HouseholdDetailView.as_view()),
]