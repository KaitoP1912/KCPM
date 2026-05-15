from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from households.models import Activity, Household, HouseholdMember, Notification
from households.serializers import (
    ActivitySerializer,
    AddHouseholdMemberSerializer,
    HouseholdSerializer,
    NotificationSerializer,
)


def get_user_display_name(user):
    return user.full_name or user.email


class HouseholdListCreateView(generics.ListCreateAPIView):
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Household.objects.filter(
            members__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        household = serializer.save(owner=self.request.user)

        HouseholdMember.objects.create(
            household=household,
            user=self.request.user,
            role=HouseholdMember.Role.OWNER
        )

        Activity.objects.create(
            household=household,
            actor=self.request.user,
            activity_type=Activity.ActivityType.GROUP_CREATED,
            title=f'{get_user_display_name(self.request.user)} đã tạo nhóm "{household.name}"',
            metadata={
                'household_id': str(household.id),
            }
        )


class HouseholdDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Household.objects.filter(
            members__user=self.request.user
        ).distinct()


class AddHouseholdMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        household = Household.objects.filter(
            id=pk,
            members__user=request.user
        ).first()

        if not household:
            return Response(
                {'detail': 'Không tìm thấy nhóm hoặc bạn không có quyền.'},
                status=status.HTTP_404_NOT_FOUND
            )

        current_member = HouseholdMember.objects.filter(
            household=household,
            user=request.user
        ).first()

        if current_member.role not in [
            HouseholdMember.Role.OWNER,
            HouseholdMember.Role.ADMIN
        ]:
            return Response(
                {'detail': 'Bạn không có quyền thêm thành viên.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AddHouseholdMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_to_add = serializer.user_to_add

        if HouseholdMember.objects.filter(
            household=household,
            user=user_to_add
        ).exists():
            return Response(
                {'detail': 'Người dùng này đã ở trong nhóm.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        member = HouseholdMember.objects.create(
            household=household,
            user=user_to_add,
            role=serializer.validated_data['role']
        )

        added_name = get_user_display_name(user_to_add)

        Activity.objects.create(
            household=household,
            actor=request.user,
            activity_type=Activity.ActivityType.MEMBER_JOINED,
            title=f'{added_name} đã được thêm vào nhóm "{household.name}"',
            metadata={
                'household_id': str(household.id),
                'added_user_id': user_to_add.id,
                'added_user_email': user_to_add.email,
            }
        )

        Notification.objects.create(
            recipient=user_to_add,
            actor=request.user,
            household=household,
            notification_type=Notification.NotificationType.ADDED_TO_GROUP,
            level=Notification.Level.IN_APP,
            title=f'Bạn đã được thêm vào nhóm "{household.name}"',
            metadata={
                'household_id': str(household.id),
                'added_by_user_id': request.user.id,
            }
        )

        old_members = HouseholdMember.objects.filter(
            household=household
        ).exclude(
            user=user_to_add
        )

        for old_member in old_members:
            Notification.objects.create(
                recipient=old_member.user,
                actor=request.user,
                household=household,
                notification_type=Notification.NotificationType.MEMBER_ADDED_TO_GROUP,
                level=Notification.Level.IN_APP,
                title=f'{added_name} đã được thêm vào nhóm "{household.name}"',
                metadata={
                    'household_id': str(household.id),
                    'added_user_id': user_to_add.id,
                }
            )

        return Response(
            {
                'id': member.id,
                'email': member.user.email,
                'role': member.role,
                'message': 'Thêm thành viên thành công.'
            },
            status=status.HTTP_201_CREATED
        )


class ActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        household_id = self.kwargs['household_id']

        return Activity.objects.filter(
            household_id=household_id,
            household__members__user=self.request.user
        ).select_related(
            'actor',
            'household'
        ).distinct().order_by('-created_at')


class AllActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(
            household__members__user=self.request.user
        ).select_related(
            'actor',
            'household'
        ).distinct().order_by('-created_at')


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            'actor',
            'household'
        ).order_by('-created_at')


class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        return Response(
            {'unread_count': count},
            status=status.HTTP_200_OK
        )


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        notification = Notification.objects.filter(
            id=pk,
            recipient=request.user
        ).first()

        if not notification:
            return Response(
                {'detail': 'Không tìm thấy thông báo.'},
                status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save(update_fields=['is_read'])

        return Response(
            {'message': 'Đã đánh dấu là đã đọc.'},
            status=status.HTTP_200_OK
        )


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        return Response(
            {'message': 'Đã đánh dấu tất cả là đã đọc.'},
            status=status.HTTP_200_OK
        )