from django.urls import path

from households.views import HouseholdListCreateView


urlpatterns = [
    path(
        '',
        HouseholdListCreateView.as_view()
    ),
]