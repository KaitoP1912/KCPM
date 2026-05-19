from django.db import transaction

from rest_framework import generics
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
    JoinHouseholdSerializer,
)


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
        ).distinct()

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

        household = Household.objects.filter(
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

        HouseholdMember.objects.create(
            household=household,
            user=request.user,
            role=HouseholdMember.Role.MEMBER
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


class ActivityListView(
    generics.ListAPIView
):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

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