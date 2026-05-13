from django.contrib import admin

from expenses.models import Debt, Expense, ExpenseParticipant


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'amount',
        'payer',
        'household',
        'split_type',
        'expense_date',
    ]
    search_fields = ['title', 'payer__email', 'household__name']
    list_filter = ['split_type', 'expense_date']


@admin.register(ExpenseParticipant)
class ExpenseParticipantAdmin(admin.ModelAdmin):
    list_display = ['expense', 'user', 'share_amount']
    search_fields = ['expense__title', 'user__email']


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = [
        'from_user',
        'to_user',
        'amount',
        'household',
        'is_paid',
    ]
    search_fields = [
        'from_user__email',
        'to_user__email',
        'household__name',
    ]
    list_filter = ['is_paid']