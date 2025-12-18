"""
Communication Django ORM Models
"""
from django.db import models
from django.conf import settings


class NotificationModel(models.Model):
    """User notification"""
    
    class NotificationType(models.TextChoices):
        LESSON_CREATED = 'LESSON_CREATED', 'Bài học mới'
        ASSIGNMENT_CREATED = 'ASSIGNMENT_CREATED', 'Bài tập mới'
        ASSIGNMENT_DEADLINE = 'ASSIGNMENT_DEADLINE', 'Bài tập sắp đến hạn'
        ASSIGNMENT_GRADED = 'ASSIGNMENT_GRADED', 'Bài tập đã được chấm'
        GENERAL = 'GENERAL', 'Thông báo chung'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=255, verbose_name='Tiêu đề')
    message = models.TextField(verbose_name='Nội dung')
    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
        verbose_name='Loại thông báo'
    )
    is_read = models.BooleanField(default=False, verbose_name='Đã đọc')
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Loại đối tượng liên quan',
        help_text='Ví dụ: lesson, assignment'
    )
    related_object_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='ID đối tượng liên quan'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian tạo')
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Thông báo'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['related_object_type', 'related_object_id']),
        ]
    
    def __str__(self):
        status = 'Đã đọc' if self.is_read else 'Chưa đọc'
        return f"{self.user.username} - {self.title} ({status})"


class CommentModel(models.Model):
    """Comment on a lesson or assignment"""
    
    class TargetType(models.TextChoices):
        LESSON = 'LESSON', 'Bài học'
        ASSIGNMENT = 'ASSIGNMENT', 'Bài tập'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Người dùng'
    )
    content = models.TextField(verbose_name='Nội dung')
    target_type = models.CharField(
        max_length=20,
        choices=TargetType.choices,
        blank=True,
        null=True,
        verbose_name='Loại đối tượng'
    )
    target_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='ID đối tượng'
    )
    # Giữ lại lesson field để backward compatibility, nhưng sẽ deprecated
    lesson = models.ForeignKey(
        'LessonModel',
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
        verbose_name='Bài học (deprecated)'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        blank=True,
        null=True,
        verbose_name='Bình luận cha'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Thời gian cập nhật')
    
    class Meta:
        db_table = 'comments'
        verbose_name = 'Bình luận'
        verbose_name_plural = 'Bình luận'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['target_type', 'target_id']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        if self.target_type and self.target_id:
            target_name = f"{self.get_target_type_display()} #{self.target_id}"
        elif self.lesson:
            target_name = f"Lesson #{self.lesson_id}"
        else:
            target_name = "Unknown"
        return f"{self.user.username} - {target_name}: {preview}"

