from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.db import transaction, IntegrityError, models
from firebase_admin import auth as firebase_auth
from django.utils.translation import gettext_lazy as _
from core.institution.models import Institution  # Import the Institution model
from core.users.services.firebase_service import FirebaseAuthService


class CustomUserManager(BaseUserManager):
    """Custom manager for User model with Firebase integration."""

    def _create_user(self, email, password, is_staff=False, is_superuser=False, firebase_uid=None):
        """
        Internal method to handle user creation.
        This is used by both `create_user` and `create_superuser`.
        """
        if not email:
            raise ValueError(_("The Email field must be set"))

        email = self.normalize_email(email)

        try:
            with transaction.atomic():
                # Create the Django user
                user: User = self.model(
                    email=email,
                    firebase_uid=firebase_uid,
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                )
                user.set_password(password)
                user.save(using=self._db)

                # Assign the "student" role by default if not superuser
                if not is_superuser:
                    student_group, _ = Group.objects.get_or_create(name="student")
                    user.groups.add(student_group)
                else:
                    # Assign the "superuser" role
                    superuser_group, _ = Group.objects.get_or_create(name="superuser")
                    user.groups.add(superuser_group)
                user.save()
                return user

        except Exception as e:
            raise IntegrityError(e)
    def create_user(self, email, password=None, **extra_fields):
        """
        Create a regular user with student role and Firebase integration.
        """
        print("this is called")
        return self._create_user(email, password, is_staff=False, is_superuser=False)

    def create_superuser(self, email, password=None):
        """
        Create a superuser with Firebase integration.
        """
        return self._create_user(email, password, is_staff=True, is_superuser=True)



class User(AbstractUser):
    """Custom User model with email as the unique identifier."""

    username = None  # Remove the default username field
    email = models.EmailField(unique=True)
    firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)

    institutions = models.ManyToManyField(
        Institution,
        through="UserInstitution",  # Specify the through model
        related_name="users",  # Backward relationship from Institution to User
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # No additional fields are required for superuser creation

    objects = CustomUserManager()


    def __str__(self):
        return self.email


class UserInstitution(models.Model):
    """Intermediate model for User-Institution relationship."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_institution_links")
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="institution_user_links")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "institution")  # Ensure unique user-institution pair

    def __str__(self):
        return f"{self.user.email} at {self.institution.name}"
