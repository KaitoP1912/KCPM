from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'household',
        'payer',
        'receiver',
        'amount',
        'status',
        'created_at',
        'confirmed_at',
        'rejected_at',
    ]

    list_filter = [
        'status',
        'household',
        'created_at',
    ]

    search_fields = [
        'payer__email',
        'receiver__email',
        'household__name',
        'debt__expense__title',
    ]

    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'confirmed_at',
        'rejected_at',
    ]
