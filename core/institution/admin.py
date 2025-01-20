# core/institutions/admin.py
from django.contrib import admin
from core.institution.models import Institution, UserInstitution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)


@admin.register(UserInstitution)
class UserInstitutionAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "created_at")
    search_fields = ("user__email", "institution__name")
    list_filter = ("institution",)
