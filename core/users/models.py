from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.db import transaction, IntegrityError, models
from firebase_admin import auth as firebase_auth
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom manager for User model with Firebase integration."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))

        email = self.normalize_email(email)

        try:
            with transaction.atomic():
                # Create user in Firebase
                firebase_user = firebase_auth.create_user(
                    email=email,
                    password=password,
                )

                # Add Firebase UID to extra_fields
                extra_fields["firebase_uid"] = firebase_user.uid

                # Create user in Django
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)

                # Assign the "student" role by default
                student_group, _ = Group.objects.get_or_create(name="student")
                user.groups.add(student_group)
                user.save()

                return user

        except Exception as e:
            # Roll back Firebase user creation if Django user creation fails
            if "firebase_user" in locals():  # Check if Firebase user was created
                firebase_auth.delete_user(firebase_user.uid)
            raise IntegrityError(
                ("Failed to create user: {}").format(str(e))
            )

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with Firebase integration."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as the unique identifier."""

    username = None  # Remove the default username field
    email = models.EmailField(unique=True)
    firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # No additional fields are required for superuser creation

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Ensure all users are added to the student group by default."""
        super().save(*args, **kwargs)  # Save the user first
        if not self.groups.exists():  # Check if the user has no group
            student_group, _ = Group.objects.get_or_create(name="student")
            self.groups.add(student_group)
