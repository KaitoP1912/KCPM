from django.conf import settings
from django.db import models

from core.models import BaseModel


class Household(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='households/',
        blank=True,
        null=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_households'
    )

    def __str__(self):
        return self.name


class HouseholdMember(BaseModel):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Chủ nhóm'
        ADMIN = 'admin', 'Quản trị viên'
        MEMBER = 'member', 'Thành viên'

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='household_memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('household', 'user')

    def __str__(self):
        return f'{self.user.email} - {self.household.name}'