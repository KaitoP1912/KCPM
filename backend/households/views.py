from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import transaction

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response
from rest_framework.views import APIView

from households.models import (
    Activity,
    Household,
    HouseholdMember,
)

from households.serializers import (
    ActivitySerializer,
    HouseholdSerializer,
    HouseholdSummarySerializer,
    JoinHouseholdSerializer,
)

User = get_user_model()


class HouseholdListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Household.objects.filter(
            is_active=True,
            members__user=self.request.user
        ).prefetch_related(
            'members',
            'members__user',
        ).distinct().order_by('-updated_at')

    @transaction.atomic
    def perform_create(self, serializer):
        household = serializer.save(
            owner=self.request.user
        )

        HouseholdMember.objects.create(
            household=household,
            user=self.request.user,
            role=HouseholdMember.Role.OWNER
        )

        Activity.objects.create(
            household=household,
            actor=self.request.user,
            activity_type=(
                Activity.ActivityType
                .MEMBER_JOINED
            ),
            title=(
                f'{self.request.user.email} '
                f'đã tạo nhóm'
            ),
        )

class HouseholdSummaryListView(
    generics.ListAPIView
):
    serializer_class = HouseholdSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Household.objects.filter(
            is_active=True,
            members__user=self.request.user
        ).prefetch_related(
            'members',
            'expenses',
            'debts',
            'activities',
        ).distinct().order_by('-updated_at')

class HouseholdDetailView(
    generics.RetrieveAPIView
):
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Household.objects.filter(
            is_active=True,
            members__user=self.request.user
        ).prefetch_related(
            'members',
            'members__user',
        ).distinct()


class JoinHouseholdView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = (
            JoinHouseholdSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        invite_code = serializer.validated_data[
            'invite_code'
        ]

        household = Household.objects.select_for_update().filter(
            invite_code=invite_code,
            is_active=True
        ).first()

        if not household:
            return Response(
                {
                    'detail':
                    'Mã mời không hợp lệ.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        existing_member = (
            HouseholdMember.objects.filter(
                household=household,
                user=request.user
            ).exists()
        )

        if existing_member:
            return Response(
                {
                    'detail':
                    'Bạn đã ở trong nhóm.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            HouseholdMember.objects.create(
                household=household,
                user=request.user,
                role=HouseholdMember.Role.MEMBER
            )
        except IntegrityError:
            return Response(
                {
                    'detail':
                    'Bạn đã ở trong nhóm.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        Activity.objects.create(
            household=household,
            actor=request.user,
            activity_type=(
                Activity.ActivityType
                .MEMBER_JOINED
            ),
            title=(
                f'{request.user.email} '
                f'đã tham gia nhóm'
            ),
        )

        household.refresh_from_db()

        response_serializer = (
            HouseholdSerializer(
                household,
                context={
                    'request': request
                }
            )
        )

        return Response(
            {
                'message':
                'Tham gia nhóm thành công.',
                'household':
                response_serializer.data
            },
            status=status.HTTP_200_OK
        )


class AddHouseholdMemberView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, household_id):
        email = (
            request.data.get('email', '')
            .strip()
            .lower()
        )

        role = request.data.get(
            'role',
            HouseholdMember.Role.MEMBER
        )

        if not email:
            return Response(
                {
                    'detail':
                    'Vui lòng nhập email thành viên.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if role not in [
            HouseholdMember.Role.MEMBER,
            HouseholdMember.Role.OWNER,
        ]:
            return Response(
                {
                    'detail':
                    'Vai trò thành viên không hợp lệ.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        household = Household.objects.select_for_update().filter(
            id=household_id,
            is_active=True,
            members__user=request.user,
        ).first()

        if not household:
            return Response(
                {
                    'detail': 'Không tìm thấy nhóm hoặc bạn không thuộc nhóm này.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        user = User.objects.filter(
            email__iexact=email
        ).first()

        if not user:
            return Response(
                {
                    'detail':
                    'Không tìm thấy tài khoản với email này.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if HouseholdMember.objects.filter(
            household=household,
            user=user
        ).exists():
            return Response(
                {
                    'detail':
                    'Người này đã ở trong nhóm.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            HouseholdMember.objects.create(
                household=household,
                user=user,
                role=role,
            )
        except IntegrityError:
            return Response(
                {
                    'detail':
                    'Người này đã ở trong nhóm.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        Activity.objects.create(
            household=household,
            actor=request.user,
            activity_type=(
                Activity.ActivityType
                .MEMBER_JOINED
            ),
            title=(
                f'{request.user.email} '
                f'đã thêm {user.email} vào nhóm'
            ),
            metadata={
                'added_user_email': user.email,
                'role': role,
            },
        )

        household.refresh_from_db()

        response_serializer = HouseholdSerializer(
            household,
            context={
                'request': request
            }
        )

        return Response(
            {
                'message': 'Đã thêm thành viên.',
                'household': response_serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        household_id = self.kwargs[
            'household_id'
        ]

        return Activity.objects.filter(
            household_id=household_id,
            household__members__user=(
                self.request.user
            )
        ).select_related(
            'actor',
            'household'
        ).order_by('-created_at')


class AllActivityListView(
    generics.ListAPIView
):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(
            household__members__user=(
                self.request.user
            )
        ).select_related(
            'actor',
            'household'
        ).order_by('-created_at')

class LeaveHouseholdView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, household_id):
        household = Household.objects.select_for_update().filter(
            id=household_id,
            is_active=True,
            members__user=request.user,
        ).first()

        if not household:
            return Response(
                {
                    'detail': 'Không tìm thấy nhóm hoặc bạn không thuộc nhóm này.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        membership = HouseholdMember.objects.select_for_update().filter(
            household=household,
            user=request.user,
        ).first()

        if not membership:
            return Response(
                {
                    'detail': 'Bạn không thuộc nhóm này.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        member_count = HouseholdMember.objects.filter(
            household=household
        ).count()

        if (
            membership.role == HouseholdMember.Role.OWNER
            and member_count > 1
        ):
            return Response(
                {
                    'detail': 'Chủ nhóm không thể rời khi nhóm còn thành viên khác.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        Activity.objects.create(
            household=household,
            actor=request.user,
            activity_type=Activity.ActivityType.MEMBER_JOINED,
            title=f'{request.user.email} đã rời nhóm',
            metadata={
                'action': 'member_left',
                'user_email': request.user.email,
            },
        )

        membership.delete()

        if member_count == 1:
            household.is_active = False
            household.save(update_fields=['is_active', 'updated_at'])

        return Response(
            {
                'message': 'Bạn đã rời nhóm.'
            },
            status=status.HTTP_200_OK
        )