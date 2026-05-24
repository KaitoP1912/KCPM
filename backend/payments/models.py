from django.conf import settings
from django.db import models

from core.models import BaseModel
from expenses.models import Debt
from households.models import Household


class Payment(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Chờ xác nhận'
        CONFIRMED = 'confirmed', 'Đã xác nhận'
        REJECTED = 'rejected', 'Đã từ chối'

    debt = models.ForeignKey(
        Debt,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_sent'
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_received'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    payer_note = models.TextField(blank=True)
    receiver_note = models.TextField(blank=True)

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    rejected_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['debt'],
                condition=models.Q(status='pending'),
                name='unique_pending_payment_per_debt'
            )
        ]

    def __str__(self):
        return (
            f'{self.payer.email} -> {self.receiver.email} '
            f'{self.amount} ({self.status})'
        )
