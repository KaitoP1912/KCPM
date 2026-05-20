from rest_framework import generics, permissions

from expenses.models import Debt, Expense
from expenses.serializers import (
    DebtSerializer,
    ExpenseCreateSerializer,
    ExpenseListSerializer,
)
from collections import defaultdict
from households.models import HouseholdMember

class ExpenseCreateView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class ExpenseListView(generics.ListAPIView):
    serializer_class = ExpenseListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        household_id = self.kwargs['household_id']

        if not HouseholdMember.objects.filter(
            household_id=household_id,
            user=self.request.user
        ).exists():
            return Expense.objects.none()

        return Expense.objects.filter(
            household_id=household_id
        ).select_related(
            'payer'
        ).order_by('-created_at')

class DebtListView(generics.ListAPIView):
    serializer_class = DebtSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        household_id = self.kwargs['household_id']
        current_user = self.request.user

        if not HouseholdMember.objects.filter(
            household_id=household_id,
            user=current_user
        ).exists():
            return Debt.objects.none()

        debts = Debt.objects.filter(
            household_id=household_id,
            is_paid=False
        ).filter(
            from_user=current_user
        ) | Debt.objects.filter(
            household_id=household_id,
            is_paid=False
        ).filter(
            to_user=current_user
        )

        balance_map = defaultdict(float)

        for debt in debts:
            key = (
                debt.from_user_id,
                debt.to_user_id,
            )

            reverse_key = (
                debt.to_user_id,
                debt.from_user_id,
            )

            if reverse_key in balance_map:
                balance_map[reverse_key] -= float(debt.amount)
            else:
                balance_map[key] += float(debt.amount)

        final_debts = []

        for (from_user_id, to_user_id), amount in balance_map.items():
            if amount <= 0:
                continue

            debt = debts.filter(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            ).first()

            if debt:
                debt.amount = amount
                final_debts.append(debt)

        return final_debts