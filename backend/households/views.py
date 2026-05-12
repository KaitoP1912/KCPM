from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from households.models import Household, HouseholdMember
from households.serializers import HouseholdSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from households.serializers import AddHouseholdMemberSerializer


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

        return Response(
            {
                'id': member.id,
                'email': member.user.email,
                'role': member.role,
                'message': 'Thêm thành viên thành công.'
            },
            status=status.HTTP_201_CREATED
        )