from django.urls import path

from expenses.views import (
    ExpenseCreateView,
    ExpenseListView,
    DebtListView,
)

urlpatterns = [
    path(
        '',
        ExpenseCreateView.as_view(),
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