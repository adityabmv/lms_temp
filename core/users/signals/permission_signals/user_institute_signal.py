from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.users.models import UserInstitution
from core.users.permissions.user_institute_permission import InstitutionPermissionManager
import logging

# Get a logger instance for this module
logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserInstitution)
def assign_permissions_on_save(sender, instance, created, **kwargs):
    """
    Assign object-level permissions when a UserInstitution instance is created or updated.

    :param sender: Model class
    :param instance: UserInstitution instance
    :param created: Boolean indicating if the instance was created
    """
    if created:
        roles = instance.user.groups.values_list("name", flat=True)  # Get all role names
        logger.info(
            f"*** [Signal: post_save] Assigning permissions for user '{instance.user.email}' and institution '{instance.institution.name}' [Roles: {roles}] ***"
        )
        InstitutionPermissionManager.assign_permissions(instance.user, instance.institution, roles)
        logger.info(f"*** [Signal: post_save] Permissions assigned successfully ***")


@receiver(post_delete, sender=UserInstitution)
def remove_permissions_on_delete(sender, instance, **kwargs):
    """
    Remove object-level permissions when a UserInstitution instance is deleted.

    :param sender: Model class
    :param instance: UserInstitution instance
    """
    roles = instance.user.groups.values_list("name", flat=True)
    logger.info(
        f"*** [Signal: post_delete] Removing permissions for user '{instance.user.email}' and institution '{instance.institution.name}' ***"
    )
    InstitutionPermissionManager.remove_permissions(instance.user, instance.institution, roles)
    logger.info(f"*** [Signal: post_delete] Permissions removed successfully ***")
