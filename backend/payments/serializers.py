from rest_framework import serializers

from payments.models import Payment


VIRTUAL_MEMBER_EMAIL_DOMAIN = '@virtual.chungvi.local'


def is_virtual_user(user):
    email = (getattr(user, 'email', '') or '').lower()
    return email.endswith(VIRTUAL_MEMBER_EMAIL_DOMAIN)


def get_user_display_name(user):
    if is_virtual_user(user):
        return user.full_name or 'Thành viên ảo'

    return user.full_name or user.email


class PaymentActionSerializer(serializers.Serializer):
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )


class PaymentSerializer(serializers.ModelSerializer):
    debt_id = serializers.UUIDField(
        source='debt.id',
        read_only=True
    )

    household_id = serializers.UUIDField(
        source='household.id',
        read_only=True
    )

    household_name = serializers.CharField(
        source='household.name',
        read_only=True
    )

    expense_id = serializers.UUIDField(
        source='debt.expense.id',
        read_only=True
    )

    expense_title = serializers.CharField(
        source='debt.expense.title',
        read_only=True
    )

    payer_id = serializers.IntegerField(
        source='payer.id',
        read_only=True
    )

    payer_name = serializers.SerializerMethodField()

    payer_email = serializers.EmailField(
        source='payer.email',
        read_only=True
    )

    receiver_id = serializers.IntegerField(
        source='receiver.id',
        read_only=True
    )

    receiver_name = serializers.SerializerMethodField()

    receiver_email = serializers.EmailField(
        source='receiver.email',
        read_only=True
    )

    status_label = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'debt_id',
            'household_id',
            'household_name',
            'expense_id',
            'expense_title',
            'payer_id',
            'payer_name',
            'payer_email',
            'receiver_id',
            'receiver_name',
            'receiver_email',
            'amount',
            'status',
            'status_label',
            'payer_note',
            'receiver_note',
            'confirmed_at',
            'rejected_at',
            'created_at',
            'updated_at',
        ]

    def get_payer_name(self, obj):
        return get_user_display_name(obj.payer)

    def get_receiver_name(self, obj):
        return get_user_display_name(obj.receiver)
