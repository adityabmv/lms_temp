from django.db import models


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

    def __str__(self):
        return self.name + (" (active)" if self.is_active else "(inactive)")
