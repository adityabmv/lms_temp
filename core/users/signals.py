from django.db.models.signals import m2m_changed
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_delete
from firebase_admin import auth as firebase_auth
from .models import User

@receiver(m2m_changed, sender=User.groups.through)
def update_user_staff_status(sender, instance, action, **kwargs):
    """
    Update is_staff and is_superuser when groups are modified.
    Automatically remove is_staff and is_superuser if user is removed from relevant groups.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        admin_roles = ["superuser", "admin", "moderator"]

        # Fetch updated group memberships
        user_groups = Group.objects.filter(user=instance).values_list("name", flat=True)

        # Update is_staff and is_superuser based on group
        instance.is_staff = any(group in admin_roles for group in user_groups)
        instance.is_superuser = "superuser" in user_groups
        instance.save()




@receiver(post_delete, sender=User)
def delete_user_from_firebase(sender, instance, **kwargs):
    """
    Deletes the user from Firebase when the user is deleted from Django.
    """
    if instance.firebase_uid:
        try:
            firebase_auth.delete_user(instance.firebase_uid)
            print(f"Firebase user with UID {instance.firebase_uid} deleted successfully.")
        except firebase_auth.UserNotFoundError:
            print(f"Firebase user with UID {instance.firebase_uid} not found.")
        except Exception as e:
            print(f"Error deleting Firebase user: {e}")
