from decimal import Decimal

from rest_framework import serializers

from accounts.models import User
from expenses.models import Debt, Expense, ExpenseParticipant
from households.models import Activity


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

    def create(self, validated_data):
        participants_data = validated_data.pop('participants')

        expense = Expense.objects.create(**validated_data)

        Activity.objects.create(
            household=expense.household,
            actor=expense.payer,
            activity_type=Activity.ActivityType.EXPENSE_CREATED,
            title=f'{expense.payer.email} đã thêm khoản chi "{expense.title}"',
            amount=expense.amount,
            metadata={
                'expense_id': str(expense.id)
            }
        )

        participant_users = []

        for item in participants_data:
            user = User.objects.get(id=item['user_id'])
            participant_users.append(user)

        split_amount = Decimal(expense.amount / len(participant_users))

        for user in participant_users:
            ExpenseParticipant.objects.create(
                expense=expense,
                user=user,
                share_amount=split_amount
            )

            if user != expense.payer:
                Debt.objects.create(
                    household=expense.household,
                    expense=expense,
                    from_user=user,
                    to_user=expense.payer,
                    amount=split_amount
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

    class Meta:
        model = Expense
        fields = [
            'id',
            'title',
            'amount',
            'payer_name',
            'payer_email',
            'expense_date',
            'note',
        ]


class DebtSerializer(serializers.ModelSerializer):
    from_user_name = serializers.CharField(
        source='from_user.full_name',
        read_only=True
    )
    from_user_email = serializers.EmailField(
        source='from_user.email',
        read_only=True
    )
    to_user_name = serializers.CharField(
        source='to_user.full_name',
        read_only=True
    )
    to_user_email = serializers.EmailField(
        source='to_user.email',
        read_only=True
    )

    class Meta:
        model = Debt
        fields = [
            'id',
            'from_user_name',
            'from_user_email',
            'to_user_name',
            'to_user_email',
            'amount',
            'is_paid',
        ]