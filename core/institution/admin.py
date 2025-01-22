from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from core.users.models import Institution
from guardian.shortcuts import get_objects_for_user

from core.users.permissions.user_institute_permission import InstitutionPermissionManager


@admin.register(Institution)
class InstitutionAdmin(GuardedModelAdmin):

    list_display = ("name", "description", "is_active")

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name="student").exists():
            return InstitutionPermissionManager.get_objects(request.user)

    def has_module_permission(self, request):
        return InstitutionPermissionManager.has_permission(request.user, "institution.view_institution")

    def has_add_permission(self, request, obj=None):
        return InstitutionPermissionManager.has_permission(request.user, "add_institution", obj)

    def has_view_permission(self, request, obj=None):
        '''This is special case, because when django admin opens, it will call permission manager function without obj,
        and it will return False, because the permission view_institution_object only exists if there is an object,
        so it will return False.
        '''
        return (
            InstitutionPermissionManager.has_permission(
                request.user,
                "view_institution_object",
                obj
            ) or
            self.has_module_permission(request)
        )

    def has_change_permission(self, request, obj=None):
        return InstitutionPermissionManager.has_permission(request.user, "change_institution_object", obj)

    def has_delete_permission(self, request, obj=None):
        return InstitutionPermissionManager.has_permission(request.user, "delete_institution_object", obj)
