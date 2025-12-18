"""
Enrollment Django ORM Model
"""
from django.db import models
from django.contrib.auth.models import User


class EnrollmentModel(models.Model):
    """Enrollment - User-Course relationship"""
    
    class CourseRole(models.TextChoices):
        TEACHER = "TEACHER", "Giáo viên"
        STUDENT = "STUDENT", "Học viên"
        TA = "TA", "Trợ giảng"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        'CourseModel',
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    role_in_course = models.CharField(
        max_length=20,
        choices=CourseRole.choices,
        default=CourseRole.STUDENT,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Đăng ký khóa học'
        verbose_name_plural = 'Đăng ký khóa học'
        unique_together = [['user', 'course']]
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.get_role_in_course_display()})"

