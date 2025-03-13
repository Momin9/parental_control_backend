from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    is_parent = models.BooleanField(default=False)
    is_child = models.BooleanField(default=False)
    # Override groups and user_permissions with custom related names
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="custom_user_set",  # Changed from default "user_set"
        related_query_name="custom_user",
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="custom_user_permissions_set",  # Changed from default "user_set"
        related_query_name="custom_user_permission",
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )


class Child(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='child')
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    last_location = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.user.username


class BlockedURL(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_urls')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='blocked_urls')
    url = models.URLField()
    blocked_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.url} blocked for {self.child.user.username}"
