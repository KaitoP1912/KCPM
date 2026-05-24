from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from expenses.models import Debt
from notifications.models import Notification
from notifications.services import create_notification
from payments.models import Payment
from payments.serializers import (
    PaymentActionSerializer,
    PaymentSerializer,
)


def get_user_display_name(user):
    return user.full_name or user.email


def format_money(amount):
    return f'{amount:,.0f}đ'.replace(',', '.')


class PaymentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MarkDebtPaidView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, debt_id):
        action_serializer = PaymentActionSerializer(
            data=request.data
        )
        action_serializer.is_valid(raise_exception=True)

        try:
            debt = Debt.objects.select_for_update().select_related(
                'household',
                'expense',
                'from_user',
                'to_user',
            ).get(id=debt_id)
        except Debt.DoesNotExist:
            return Response(
                {'detail': 'Không tìm thấy công nợ.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if debt.from_user_id != request.user.id:
            raise PermissionDenied(
                'Chỉ người đang nợ mới có thể báo đã thanh toán.'
            )

        if debt.is_paid:
            return Response(
                {'detail': 'Công nợ này đã được thanh toán.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing_pending_payment = Payment.objects.filter(
            debt=debt,
            status=Payment.Status.PENDING
        ).select_related(
            'debt',
            'debt__expense',
            'household',
            'payer',
            'receiver',
        ).first()

        if existing_pending_payment:
            return Response(
                {
                    'message': 'Yêu cầu thanh toán đang chờ xác nhận.',
                    'payment': PaymentSerializer(
                        existing_pending_payment
                    ).data,
                },
                status=status.HTTP_200_OK
            )

        payment = Payment.objects.create(
            debt=debt,
            household=debt.household,
            payer=debt.from_user,
            receiver=debt.to_user,
            amount=debt.amount,
            payer_note=action_serializer.validated_data.get(
                'note',
                ''
            )
        )

        payer_name = get_user_display_name(payment.payer)

        create_notification(
            recipient=payment.receiver,
            actor=payment.payer,
            household=payment.household,
            notification_type=Notification.NotificationType.PAYMENT_RECEIVED,
            level=Notification.Level.PUSH,
            title=(
                f'{payer_name} báo đã thanh toán '
                f'{format_money(payment.amount)} cho khoản '
                f'"{debt.expense.title}". Vui lòng xác nhận.'
            ),
            amount=payment.amount,
            metadata={
                'payment_id': str(payment.id),
                'debt_id': str(debt.id),
                'expense_id': str(debt.expense_id),
                'status': payment.status,
            },
            push_title='Xác nhận thanh toán',
            push_body=(
                f'{payer_name} báo đã thanh toán '
                f'{format_money(payment.amount)}'
            ),
        )

        return Response(
            {
                'message': 'Đã gửi yêu cầu xác nhận thanh toán.',
                'payment': PaymentSerializer(payment).data,
            },
            status=status.HTTP_201_CREATED
        )


class PendingPaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaymentPagination

    def get_queryset(self):
        return Payment.objects.filter(
            receiver=self.request.user,
            status=Payment.Status.PENDING
        ).select_related(
            'debt',
            'debt__expense',
            'household',
            'payer',
            'receiver',
        ).order_by('-created_at')


class MyPaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaymentPagination

    def get_queryset(self):
        return Payment.objects.filter(
            Q(payer=self.request.user) |
            Q(receiver=self.request.user)
        ).select_related(
            'debt',
            'debt__expense',
            'household',
            'payer',
            'receiver',
        ).order_by('-created_at')


class ConfirmPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        action_serializer = PaymentActionSerializer(
            data=request.data
        )
        action_serializer.is_valid(raise_exception=True)

        try:
            payment = Payment.objects.select_for_update().select_related(
                'debt',
                'debt__expense',
                'household',
                'payer',
                'receiver',
            ).get(id=pk)
        except Payment.DoesNotExist:
            return Response(
                {'detail': 'Không tìm thấy yêu cầu thanh toán.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if payment.receiver_id != request.user.id:
            raise PermissionDenied(
                'Chỉ người nhận tiền mới có thể xác nhận thanh toán.'
            )

        if payment.status != Payment.Status.PENDING:
            return Response(
                {
                    'detail':
                    'Yêu cầu thanh toán này không còn chờ xác nhận.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.debt.is_paid = True
        payment.debt.save(
            update_fields=['is_paid', 'updated_at']
        )

        payment.status = Payment.Status.CONFIRMED
        payment.receiver_note = action_serializer.validated_data.get(
            'note',
            ''
        )
        payment.confirmed_at = timezone.now()
        payment.save(
            update_fields=[
                'status',
                'receiver_note',
                'confirmed_at',
                'updated_at',
            ]
        )

        receiver_name = get_user_display_name(payment.receiver)

        create_notification(
            recipient=payment.payer,
            actor=payment.receiver,
            household=payment.household,
            notification_type=Notification.NotificationType.PAYMENT_SENT,
            level=Notification.Level.PUSH,
            title=(
                f'{receiver_name} đã xác nhận nhận '
                f'{format_money(payment.amount)}.'
            ),
            amount=payment.amount,
            metadata={
                'payment_id': str(payment.id),
                'debt_id': str(payment.debt_id),
                'expense_id': str(payment.debt.expense_id),
                'status': payment.status,
            },
            push_title='Thanh toán đã được xác nhận',
            push_body=(
                f'{receiver_name} đã xác nhận nhận tiền.'
            ),
        )

        return Response(
            {
                'message': 'Đã xác nhận nhận tiền.',
                'payment': PaymentSerializer(payment).data,
            },
            status=status.HTTP_200_OK
        )


class RejectPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        action_serializer = PaymentActionSerializer(
            data=request.data
        )
        action_serializer.is_valid(raise_exception=True)

        try:
            payment = Payment.objects.select_for_update().select_related(
                'debt',
                'debt__expense',
                'household',
                'payer',
                'receiver',
            ).get(id=pk)
        except Payment.DoesNotExist:
            return Response(
                {'detail': 'Không tìm thấy yêu cầu thanh toán.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if payment.receiver_id != request.user.id:
            raise PermissionDenied(
                'Chỉ người nhận tiền mới có thể từ chối thanh toán.'
            )

        if payment.status != Payment.Status.PENDING:
            return Response(
                {
                    'detail':
                    'Yêu cầu thanh toán này không còn chờ xác nhận.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = Payment.Status.REJECTED
        payment.receiver_note = action_serializer.validated_data.get(
            'note',
            ''
        )
        payment.rejected_at = timezone.now()
        payment.save(
            update_fields=[
                'status',
                'receiver_note',
                'rejected_at',
                'updated_at',
            ]
        )

        receiver_name = get_user_display_name(payment.receiver)

        create_notification(
            recipient=payment.payer,
            actor=payment.receiver,
            household=payment.household,
            notification_type=Notification.NotificationType.PAYMENT_SENT,
            level=Notification.Level.PUSH,
            title=(
                f'{receiver_name} chưa xác nhận khoản thanh toán '
                f'{format_money(payment.amount)}.'
            ),
            amount=payment.amount,
            metadata={
                'payment_id': str(payment.id),
                'debt_id': str(payment.debt_id),
                'expense_id': str(payment.debt.expense_id),
                'status': payment.status,
            },
            push_title='Thanh toán bị từ chối',
            push_body=(
                f'{receiver_name} chưa xác nhận khoản thanh toán.'
            ),
        )

        return Response(
            {
                'message': 'Đã từ chối yêu cầu thanh toán.',
                'payment': PaymentSerializer(payment).data,
            },
            status=status.HTTP_200_OK
        )
