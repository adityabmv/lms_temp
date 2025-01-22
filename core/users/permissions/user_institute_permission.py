import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user

from core.institution.models import Institution
from core.users.models import User

# Get a logger instance for this module
logger = logging.getLogger(__name__)


class InstitutionPermissionManager:
    """Manages object-level permissions for institutions based on user roles."""
    DEFAULT_MODEL_PERMISSIONS = {
        "view_institution": "Can view institution globally",
        "add_institution": "Can add institution globally",
        "change_institution": "Can change institution globally",
        "delete_institution": "Can delete institution globally",
    }

    NEW_PERMISSIONS = {
        "view_institution_object": "Can view institution object-level",
        "change_institution_object": "Can change institution object-level",
        "delete_institution_object": "Can delete institution object-level",
    }

    ROLE_PERMISSIONS = {
        "student": ["view_institution_object","view_institution"],
        "moderator": ["view_institution_object", "change_institution_object", "add_institution", "view_institution"],
    }

    MODEL_NAME = "institution"

    @staticmethod
    def init(self):
        """
        Ensure all permissions in `ALL_PERMISSIONS` are created in the database.
        """
        content_type = ContentType.objects.get_for_model(Institution)

        for codename, name in self.NEW_PERMISSIONS.items():
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type,
            )
            if created:
                print(f"✅ Permission '{name}' created successfully.")
            else:
                print(f"ℹ️ Permission '{name}' already exists.")

    @staticmethod
    def assign_permissions(user, institution, roles):
        """
        Assign permissions to a user for a specific institution based on their roles.

        :param user: User instance
        :param institution: Institution instance
        :param roles: List of role names assigned to the user
        """
        if 'student' in roles:
            for permission in InstitutionPermissionManager.ROLE_PERMISSIONS['student']:
                if permission in InstitutionPermissionManager.DEFAULT_MODEL_PERMISSIONS:
                    print(f"Assigning model permission {permission}")
                    assign_perm(f"{InstitutionPermissionManager.MODEL_NAME}.{permission}", user)
                else:
                    print(f"Assigning object level permission {permission}")
                    assign_perm(f"{permission}", user, institution)
        if 'moderator' in roles:
            print("Assigning moderator permissions")
            for permission in InstitutionPermissionManager.ROLE_PERMISSIONS['moderator']:
                if permission in InstitutionPermissionManager.DEFAULT_MODEL_PERMISSIONS:
                    print(f"Assigning model permission {permission}")
                    assign_perm(f"{InstitutionPermissionManager.MODEL_NAME}.{permission}", user)
                else:
                    print(f"Assigning object level permission {permission}")
                    assign_perm(f"{permission}", user, institution)

    @staticmethod
    def remove_permissions(user, institution, roles):
        """
        Remove all permissions for a user on a specific institution.

        :param user: User instance
        :param institution: Institution instance
        :param roles: List of role names assigned to the user
        """
        if 'student' in roles:
            for permission in InstitutionPermissionManager.ROLE_PERMISSIONS['student']:
                if permission in InstitutionPermissionManager.DEFAULT_MODEL_PERMISSIONS:
                    remove_perm(f"{InstitutionPermissionManager.MODEL_NAME}.{permission}", user)
                else:
                    remove_perm(f"{permission}", user, institution)
        if 'moderator' in roles:
            for permission in InstitutionPermissionManager.ROLE_PERMISSIONS['moderator']:
                if permission in InstitutionPermissionManager.DEFAULT_MODEL_PERMISSIONS:
                    remove_perm(f"{InstitutionPermissionManager.MODEL_NAME}.{permission}", user)
                else:
                    remove_perm(f"{permission}", user, institution)




    @staticmethod
    def get_all_permissions():
        """
        Get all defined permissions across all roles.
        :return: List of all permission strings.
        """
        return [
            perm
            for perms in InstitutionPermissionManager.ROLE_PERMISSIONS.values()
            for perm in perms
        ]

    @staticmethod
    def has_permission(user:User, permission, object=None):
        """
        Check if a user has a specific permission.
        :param object: Institution instance
        :param user: User instance
        :param permission: Permission string
        :return: True if the user has the permission, False otherwise.
        """
        print(f"[[ {permission} ]] Checking permission")
        if user.is_superuser:
            print("User is superuser, no permission checks")
            return True
        if object:
            print(f"[[ {permission} ]] Checking permission with object", object)
            return user.has_perm(f"{permission}", object)
        else:
            print(f"[[ {permission} ]] Checking permission without object")
            print(user.has_perm(f"{permission}"))
            return user.has_perm(f"{permission}")

    @staticmethod
    def get_objects(user: User):
        """
        Return a queryset of objects for which a user has a specific permission.
        :param user: User instance
        :return: Queryset of objects
        """
        # get user roles
        user_roles = user.groups.values_list("name", flat=True)
        all_permissions = []
        for role in user_roles:
            all_permissions += InstitutionPermissionManager.ROLE_PERMISSIONS[role]
        print("All Permissions are", all_permissions)
        return get_objects_for_user(user, all_permissions, Institution.objects.all())