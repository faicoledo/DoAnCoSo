"""
User Django ORM Models
"""
import os
from django.db import models
from django.contrib.auth.models import User


class UserProfileModel(models.Model):
    """
    User Profile - extends Django User model
    """
    class GlobalRole(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Giáo viên"
        STUDENT = "STUDENT", "Học viên"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=GlobalRole.choices,
        default=GlobalRole.STUDENT,
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
    )
    bio = models.TextField(
        blank=True,
        help_text="Mô tả ngắn về người dùng",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_userprofile'  # Khớp với bảng cũ
        verbose_name = 'Hồ sơ người dùng'
        verbose_name_plural = 'Hồ sơ người dùng'

    def __str__(self) -> str:
        return f"{self.full_name} ({self.user.username})"

    def save(self, *args, **kwargs):
        # Delete old avatar when updating
        if self.pk:
            try:
                old_instance = UserProfileModel.objects.get(pk=self.pk)
                if old_instance.avatar and old_instance.avatar != self.avatar:
                    if old_instance.avatar.path and os.path.isfile(old_instance.avatar.path):
                        os.remove(old_instance.avatar.path)
            except UserProfileModel.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete avatar file when deleting profile
        if self.avatar:
            if self.avatar.path and os.path.isfile(self.avatar.path):
                os.remove(self.avatar.path)
        super().delete(*args, **kwargs)


# Add full_name property to User model
def get_user_full_name(self):
    """Return full_name from UserProfile if exists"""
    try:
        if hasattr(self, 'profile') and self.profile:
            return self.profile.full_name
    except UserProfileModel.DoesNotExist:
        pass
    return self.get_full_name() or self.username


User.add_to_class('full_name', property(get_user_full_name))

