from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from households.models import Household, HouseholdMember
from households.serializers import HouseholdSerializer


class HouseholdListCreateView(generics.ListCreateAPIView):
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Household.objects.filter(
            members__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        household = serializer.save(
            owner=self.request.user
        )

        HouseholdMember.objects.create(
            household=household,
            user=self.request.user,
            role=HouseholdMember.Role.OWNER
        )