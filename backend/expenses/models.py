from decimal import Decimal

from django.conf import settings
from django.db import models

from core.models import BaseModel
from households.models import Household


class Expense(BaseModel):
    class SplitType(models.TextChoices):
        EQUAL = 'equal', 'Chia đều'
        MANUAL = 'manual', 'Nhập thủ công'

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paid_expenses'
    )
    split_type = models.CharField(
        max_length=20,
        choices=SplitType.choices,
        default=SplitType.EQUAL
    )
    note = models.TextField(blank=True)
    expense_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} - {self.amount}'


class ExpenseParticipant(BaseModel):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_participations'
    )
    share_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=Decimal('0')
    )

    class Meta:
        unique_together = ('expense', 'user')

    def __str__(self):
        return f'{self.user.email} - {self.share_amount}'


class Debt(BaseModel):
    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='debts'
    )
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='debts'
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='debts_to_pay'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='debts_to_receive'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=0)

    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.from_user.email} owes {self.to_user.email}: {self.amount}'