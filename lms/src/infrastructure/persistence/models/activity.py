"""
Activity Django ORM Models
"""
from django.db import models
from django.conf import settings


class UserActivityLogModel(models.Model):
    """User activity log"""
    
    class ActionType(models.TextChoices):
        VIEW_LESSON = 'VIEW_LESSON', 'Xem bài học'
        START_ATTEMPT = 'START_ATTEMPT', 'Bắt đầu làm bài'
        SUBMIT_ATTEMPT = 'SUBMIT_ATTEMPT', 'Nộp bài'
        VIEW_RESULT = 'VIEW_RESULT', 'Xem kết quả bài làm'
        VIEW_RESOURCE = 'VIEW_RESOURCE', 'Xem tài liệu'
        PLAY_VIDEO = 'PLAY_VIDEO', 'Phát video'
        VIEW_COURSE = 'VIEW_COURSE', 'Xem khóa học'
        VIEW_MODULE = 'VIEW_MODULE', 'Xem chương'
        COMMENT = 'COMMENT', 'Bình luận'
        DOWNLOAD_RESOURCE = 'DOWNLOAD_RESOURCE', 'Tải tài liệu'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name='Người dùng'
    )
    action_type = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        verbose_name='Loại hành động'
    )
    target_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Loại đối tượng',
        help_text='Ví dụ: lesson, assignment, attempt'
    )
    target_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='ID đối tượng'
    )
    # Giữ lại course field để backward compatibility
    course = models.ForeignKey(
        'CourseModel',
        on_delete=models.CASCADE,
        related_name='activity_logs',
        blank=True,
        null=True,
        verbose_name='Khóa học (deprecated)'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name='Metadata',
        help_text='Thông tin bổ sung: điểm số, attempt_id, etc.'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian')
    
    class Meta:
        db_table = 'user_activity_logs'
        verbose_name = 'Nhật ký hoạt động'
        verbose_name_plural = 'Nhật ký hoạt động'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['target_type', 'target_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.timestamp}"

