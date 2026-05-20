from decimal import Decimal

from rest_framework import serializers

from accounts.models import User
from expenses.models import Debt, Expense, ExpenseParticipant
from households.models import Activity, HouseholdMember

from notifications.models import Notification
from notifications.services import create_notification

def get_user_display_name(user):
    return user.full_name or user.email


class ExpenseParticipantInputSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class ExpenseCreateSerializer(serializers.ModelSerializer):
    participants = ExpenseParticipantInputSerializer(
        many=True,
        write_only=True
    )

    class Meta:
        model = Expense
        fields = [
            'id',
            'household',
            'title',
            'amount',
            'payer',
            'split_type',
            'note',
            'participants',
        ]

    def validate(self, attrs):
        household = attrs.get('household')
        payer = attrs.get('payer')
        participants = attrs.get('participants', [])

        request = self.context.get('request')

        if not request or not HouseholdMember.objects.filter(
            household=household,
            user=request.user
        ).exists():
            raise serializers.ValidationError(
                'Bạn không có quyền thêm khoản chi vào nhóm này.'
            )

        if not participants:
            raise serializers.ValidationError(
                'Vui lòng chọn ít nhất một người tham gia chia tiền.'
            )

        if not HouseholdMember.objects.filter(
            household=household,
            user=payer
        ).exists():
            raise serializers.ValidationError(
                'Người trả tiền không thuộc nhóm này.'
            )

        participant_ids = [item['user_id'] for item in participants]

        if len(participant_ids) != len(set(participant_ids)):
            raise serializers.ValidationError(
                'Danh sách người chia tiền bị trùng.'
            )

        valid_member_count = HouseholdMember.objects.filter(
            household=household,
            user_id__in=participant_ids
        ).count()

        if valid_member_count != len(set(participant_ids)):
            raise serializers.ValidationError(
                'Danh sách người chia tiền có người không thuộc nhóm.'
            )

        return attrs

    def create(self, validated_data):
        participants_data = validated_data.pop('participants')

        expense = Expense.objects.create(**validated_data)

        payer_name = get_user_display_name(expense.payer)

        Activity.objects.create(
            household=expense.household,
            actor=expense.payer,
            activity_type=Activity.ActivityType.EXPENSE_CREATED,
            title=f'{payer_name} đã thêm khoản "{expense.title}"',
            amount=expense.amount,
            metadata={
                'expense_id': str(expense.id),
                'participant_count': len(participants_data),
            }
        )

        participant_users = []

        for item in participants_data:
            user = User.objects.get(id=item['user_id'])
            participant_users.append(user)

        total_amount = int(expense.amount)
        participant_count = len(participant_users)

        base_share = total_amount // participant_count
        remainder = total_amount % participant_count

        for index, user in enumerate(participant_users):
            split_amount = Decimal(
                base_share + (
                    remainder if index == 0 else 0
                )
            )
            ExpenseParticipant.objects.create(
                expense=expense,
                user=user,
                share_amount=split_amount
            )

            if user != expense.payer:
                debt = Debt.objects.create(
                    household=expense.household,
                    expense=expense,
                    from_user=user,
                    to_user=expense.payer,
                    amount=split_amount
                )

                create_notification(
                    recipient=user,
                    actor=expense.payer,
                    household=expense.household,

                    notification_type=(
                        Notification.NotificationType.DEBT_CREATED
                    ),

                    level=Notification.Level.PUSH,

                    title=(
                        f'{payer_name} đã thêm khoản "{expense.title}", '
                        f'bạn cần chia {split_amount:,.0f}đ'
                    ).replace(',', '.'),

                    amount=split_amount,

                    metadata={
                        'expense_id': str(expense.id),
                        'debt_id': str(debt.id),
                        'payer_id': expense.payer.id,
                        'share_amount': str(split_amount),
                    },

                    push_title='Khoản chi mới',

                    push_body=(
                        f'{payer_name} vừa thêm '
                        f'"{expense.title}"'
                    ),
                )

        return expense


class ExpenseListSerializer(serializers.ModelSerializer):
    payer_name = serializers.CharField(
        source='payer.full_name',
        read_only=True
    )

    payer_email = serializers.EmailField(
        source='payer.email',
        read_only=True
    )

    payer_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Expense

        fields = [
            'id',
            'title',
            'amount',

            'payer_name',
            'payer_email',
            'payer_avatar',

            'expense_date',
            'note',
        ]

    def get_payer_avatar(self, obj):
        request = self.context.get('request')

        if obj.payer.avatar and request:
            return request.build_absolute_uri(
                obj.payer.avatar.url
            )

        return ''

class DebtSerializer(serializers.ModelSerializer):
    from_user_name = serializers.CharField(
        source='from_user.full_name',
        read_only=True
    )

    from_user_email = serializers.EmailField(
        source='from_user.email',
        read_only=True
    )

    from_user_avatar = serializers.SerializerMethodField()

    to_user_name = serializers.CharField(
        source='to_user.full_name',
        read_only=True
    )

    to_user_email = serializers.EmailField(
        source='to_user.email',
        read_only=True
    )

    to_user_avatar = serializers.SerializerMethodField()

    bank_name = serializers.CharField(
        source='to_user.bank_name',
        read_only=True
    )

    bank_account_number = serializers.CharField(
        source='to_user.bank_account_number',
        read_only=True
    )

    bank_account_holder = serializers.CharField(
        source='to_user.bank_account_holder',
        read_only=True
    )

    class Meta:
        model = Debt

        fields = [
            'id',

            'from_user_name',
            'from_user_email',
            'from_user_avatar',

            'to_user_name',
            'to_user_email',
            'to_user_avatar',

            'bank_name',
            'bank_account_number',
            'bank_account_holder',

            'amount',
            'is_paid',
        ]

    def get_from_user_avatar(self, obj):
        request = self.context.get('request')

        if obj.from_user.avatar and request:
            return request.build_absolute_uri(
                obj.from_user.avatar.url
            )

        return ''

    def get_to_user_avatar(self, obj):
        request = self.context.get('request')

        if obj.to_user.avatar and request:
            return request.build_absolute_uri(
                obj.to_user.avatar.url
            )

        return ''