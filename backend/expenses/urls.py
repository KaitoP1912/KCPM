from django.urls import path

from expenses.views import (
    DebtListView,
    ExpenseCreateView,
    ExpenseDetailView,
    ExpenseListView,
)

urlpatterns = [
    path(
        '',
        ExpenseCreateView.as_view(),
    ),

    path(
        '<uuid:pk>/',
        ExpenseDetailView.as_view(),
    ),

    path(
        'household/<uuid:household_id>/',
        ExpenseListView.as_view(),
    ),

    path(
        'household/<uuid:household_id>/debts/',
        DebtListView.as_view(),
    ),
]