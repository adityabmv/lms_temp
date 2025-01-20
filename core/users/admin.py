from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from django.contrib.auth.models import Group


class UserAdmin(BaseUserAdmin):
    """Custom admin for the User model."""

    # Define the fields to be displayed in the admin interface
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    # Define the fieldsets for viewing and editing users
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Define the fields for adding a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )



# Unregister the default Group admin
admin.site.unregister(Group)


@admin.register(Group)
class CustomGroupAdmin(admin.ModelAdmin):
    """Custom admin for Group to move it under the Users section."""

    list_display = ("name",)  # Display the name of the group
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("permissions",)  # Allows selecting permissions in a user-friendly way

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"


# Override the default app label for Group to move it under the Users section
Group._meta.app_label = "users"  # Change app label for the Group model


# Register the custom User model and the custom UserAdmin
admin.site.register(User, UserAdmin)
