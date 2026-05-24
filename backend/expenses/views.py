from collections import defaultdict

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from expenses.models import Debt, Expense
from expenses.serializers import (
    DebtSerializer,
    ExpenseCreateUpdateSerializer,
    ExpenseDetailSerializer,
    ExpenseListSerializer,
    get_user_display_name,
    is_user_expense_manager,
)

from households.models import Activity, HouseholdMember


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ExpenseCreateView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExpenseListView(generics.ListAPIView):
    serializer_class = ExpenseListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

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
            'household',
            'payer',
        ).prefetch_related(
            'participants__user',
        ).order_by('-created_at')


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'pk'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ExpenseCreateUpdateSerializer

        return ExpenseDetailSerializer

    def get_queryset(self):
        return Expense.objects.filter(
            household__members__user=self.request.user
        ).select_related(
            'household',
            'payer',
        ).prefetch_related(
            'participants__user',
        ).distinct()

    def destroy(self, request, *args, **kwargs):
        expense = self.get_object()

        if not is_user_expense_manager(
            request.user,
            expense
        ):
            raise PermissionDenied(
                'Bạn không có quyền xóa khoản chi này.'
            )

        if expense.debts.filter(is_paid=True).exists():
            return Response(
                {
                    'detail':
                    'Không thể xóa khoản chi đã có công nợ được thanh toán.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        expense_title = expense.title
        expense_amount = expense.amount
        household = expense.household

        actor_name = get_user_display_name(request.user)

        Activity.objects.create(
            household=household,
            actor=request.user,
            activity_type=Activity.ActivityType.EXPENSE_DELETED,
            title=f'{actor_name} đã xóa khoản "{expense_title}"',
            amount=expense_amount,
            metadata={
                'expense_id': str(expense.id),
                'expense_title': expense_title,
            }
        )

        expense.delete()

        return Response(
            {
                'message': 'Xóa khoản chi thành công.'
            },
            status=status.HTTP_200_OK
        )


class DebtListView(generics.ListAPIView):
    serializer_class = DebtSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

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

        debts = debts.select_related(
            'from_user',
            'to_user',
            'household',
            'expense',
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