from django.urls import path

from payments.views import (
    ConfirmPaymentView,
    MarkDebtPaidView,
    MyPaymentListView,
    PendingPaymentListView,
    RejectPaymentView,
)

urlpatterns = [
    path(
        'debts/<uuid:debt_id>/mark-paid/',
        MarkDebtPaidView.as_view(),
    ),

    path(
        'pending/',
        PendingPaymentListView.as_view(),
    ),

    path(
        'mine/',
        MyPaymentListView.as_view(),
    ),

    path(
        '<uuid:pk>/confirm/',
        ConfirmPaymentView.as_view(),
    ),

    path(
        '<uuid:pk>/reject/',
        RejectPaymentView.as_view(),
    ),
]