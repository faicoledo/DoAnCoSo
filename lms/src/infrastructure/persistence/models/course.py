"""
Course Django ORM Models
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import date


class SubjectModel(models.Model):
    """Subject - Top level category"""
    title = models.CharField(max_length=255, verbose_name='Tên môn học')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subjects'
        verbose_name = 'Môn học'
        verbose_name_plural = 'Môn học'
        ordering = ['title']
    
    def __str__(self):
        return self.title


class CourseModel(models.Model):
    """
    Course - belongs to Subject
    
    Trạng thái khóa học được tính tự động dựa trên thời gian:
    - UPCOMING: Trước ngày bắt đầu
    - ONGOING: Trong thời gian khóa học
    - COMPLETED: Sau ngày kết thúc
    """
    
    class StatusChoices(models.TextChoices):
        UPCOMING = 'UPCOMING', 'Sắp diễn ra'
        ONGOING = 'ONGOING', 'Đang diễn ra'
        COMPLETED = 'COMPLETED', 'Đã hoàn thành'
    
    subject = models.ForeignKey(
        SubjectModel,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Môn học'
    )
    title = models.CharField(max_length=255, verbose_name='Tên khóa học')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    start_date = models.DateField(verbose_name='Ngày bắt đầu')
    end_date = models.DateField(verbose_name='Ngày kết thúc')
    # Giữ lại field status trong DB để tương thích, nhưng sẽ được tính tự động
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.UPCOMING,
        verbose_name='Trạng thái',
        editable=False,  # Không cho phép chỉnh sửa trong admin
        help_text='Trạng thái được tính tự động dựa trên ngày bắt đầu và kết thúc'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Khóa học'
        verbose_name_plural = 'Khóa học'
        ordering = ['-start_date', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.subject.title})"
    
    @property
    def computed_status(self) -> str:
        """Tính trạng thái dựa trên thời gian hiện tại"""
        if not self.start_date or not self.end_date:
            return self.StatusChoices.UPCOMING  # Default khi chưa có ngày
        
        today = date.today()
        
        if today < self.start_date:
            return self.StatusChoices.UPCOMING
        elif today > self.end_date:
            return self.StatusChoices.COMPLETED
        else:
            return self.StatusChoices.ONGOING
    
    @property
    def computed_status_display(self) -> str:
        """Hiển thị trạng thái dạng text"""
        status_map = {
            self.StatusChoices.UPCOMING: 'Sắp diễn ra',
            self.StatusChoices.ONGOING: 'Đang diễn ra',
            self.StatusChoices.COMPLETED: 'Đã hoàn thành',
        }
        return status_map.get(self.computed_status, '')
    
    @property
    def is_upcoming(self) -> bool:
        """Khóa học sắp diễn ra"""
        return self.computed_status == self.StatusChoices.UPCOMING
    
    @property
    def is_ongoing(self) -> bool:
        """Khóa học đang diễn ra"""
        return self.computed_status == self.StatusChoices.ONGOING
    
    @property
    def is_completed(self) -> bool:
        """Khóa học đã kết thúc"""
        return self.computed_status == self.StatusChoices.COMPLETED
    
    @property
    def days_until_start(self) -> int | None:
        """Số ngày còn lại đến khi bắt đầu (âm nếu đã bắt đầu)"""
        if not self.start_date:
            return None
        return (self.start_date - date.today()).days
    
    @property
    def days_until_end(self) -> int | None:
        """Số ngày còn lại đến khi kết thúc (âm nếu đã kết thúc)"""
        if not self.end_date:
            return None
        return (self.end_date - date.today()).days
    
    @property
    def duration_days(self) -> int | None:
        """Tổng số ngày của khóa học"""
        if not self.start_date or not self.end_date:
            return None
        return (self.end_date - self.start_date).days + 1
    
    def save(self, *args, **kwargs):
        """Tự động cập nhật status khi save"""
        self.status = self.computed_status
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate ngày bắt đầu phải trước ngày kết thúc"""
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({
                    'end_date': 'Ngày kết thúc phải sau ngày bắt đầu.'
                })


class ModuleModel(models.Model):
    """Module - Chapter of a Course"""
    course = models.ForeignKey(
        CourseModel,
        on_delete=models.CASCADE,
        related_name='modules',
    )
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modules'
        verbose_name = 'Chương'
        verbose_name_plural = 'Chương'
        ordering = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        """Xử lý order khi save"""
        from ..utils.order_manager import handle_order_on_save
        handle_order_on_save(self, 'course', 'order')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Sắp xếp lại order khi xóa"""
        from ..utils.order_manager import handle_order_on_delete
        handle_order_on_delete(self, 'course', 'order')
        super().delete(*args, **kwargs)


class LessonModel(models.Model):
    """Lesson - belongs to Module"""
    module = models.ForeignKey(
        ModuleModel,
        on_delete=models.CASCADE,
        related_name='lessons',
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        verbose_name = 'Bài học'
        verbose_name_plural = 'Bài học'
        ordering = ['module', 'order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        """Xử lý order khi save"""
        from ..utils.order_manager import handle_order_on_save
        is_new = self._state.adding
        handle_order_on_save(self, 'module', 'order')
        super().save(*args, **kwargs)
        
        # Gửi notification cho học viên khi tạo lesson mới
        if is_new:
            try:
                from ...application.use_cases.notification import notify_students_on_new_lesson
                course_id = self.module.course_id
                notify_students_on_new_lesson(
                    lesson_id=self.id,
                    course_id=course_id,
                )
            except Exception:
                pass  # Bỏ qua lỗi notification để không ảnh hưởng đến flow chính
    
    def delete(self, *args, **kwargs):
        """Sắp xếp lại order khi xóa"""
        from ..utils.order_manager import handle_order_on_delete
        handle_order_on_delete(self, 'module', 'order')
        super().delete(*args, **kwargs)

