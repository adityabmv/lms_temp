from django.db import models
from core.users.models import User


class Institution(models.Model):
    name = models.CharField(max_length=1000, unique=True)
    description = models.TextField(
        null=True, blank=True, max_length=3000
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=False)


class UserInstitution(models.Model):
    """Relationship between users and institutions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="institutions")
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "institution")  # Ensure unique user-institution pair

    def __str__(self):
        return f"{self.user.email} at {self.institution.name}"