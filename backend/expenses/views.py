from rest_framework import generics, permissions

from expenses.models import Debt, Expense
from expenses.serializers import (
    DebtSerializer,
    ExpenseCreateSerializer,
    ExpenseListSerializer,
)


class ExpenseCreateView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExpenseListView(generics.ListAPIView):
    serializer_class = ExpenseListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        household_id = self.kwargs['household_id']

        return Expense.objects.filter(
            household_id=household_id
        ).order_by('-created_at')


class DebtListView(generics.ListAPIView):
    serializer_class = DebtSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        household_id = self.kwargs['household_id']

        return Debt.objects.filter(
            household_id=household_id,
            is_paid=False
        )