from django.contrib import admin

from households.models import Household, HouseholdMember


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    search_fields = ['name', 'owner__email']


@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    list_display = ['household', 'user', 'role', 'joined_at']
    search_fields = ['household__name', 'user__email']
    list_filter = ['role']