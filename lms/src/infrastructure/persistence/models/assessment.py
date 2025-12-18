"""
Assessment Django ORM Models

Bao gồm:
- Assignment: Bài tập (Quiz hoặc Nộp file)
- Question: Câu hỏi trắc nghiệm (thuộc Assignment)
- Attempt: Lần làm bài của học viên
- AttemptDetail: Chi tiết câu trả lời của mỗi câu hỏi
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from ..validators import SubmissionFileValidator


class AssignmentModel(models.Model):
    """
    Assignment - Bài tập
    
    Loại bài tập:
    - QUIZ: Bài kiểm tra trắc nghiệm (có câu hỏi)
    - FILE_UPLOAD: Nộp file bài tập
    """
    
    class AssignmentType(models.TextChoices):
        QUIZ = 'QUIZ', 'Quiz'
        FILE_UPLOAD = 'FILE_UPLOAD', 'Nộp file'

    lesson = models.ForeignKey(
        'LessonModel',
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Bài học'
    )
    title = models.CharField(max_length=255, verbose_name='Tiêu đề')
    instructions = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Hướng dẫn',
        help_text='Hướng dẫn làm bài cho học viên'
    )
    type = models.CharField(
        max_length=20,
        choices=AssignmentType.choices,
        default=AssignmentType.QUIZ,
        verbose_name='Loại bài tập'
    )
    start_at = models.DateTimeField(verbose_name='Thời gian mở')
    end_at = models.DateTimeField(verbose_name='Thời gian đóng')
    time_limit = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name='Giới hạn thời gian (phút)',
        help_text='Để trống nếu không giới hạn'
    )
    attempts_allowed = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Số lần làm cho phép'
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        validators=[MinValueValidator(0)],
        verbose_name='Điểm tối đa'
    )
    shuffle_questions = models.BooleanField(
        default=False,
        verbose_name='Trộn câu hỏi',
        help_text='Trộn ngẫu nhiên thứ tự câu hỏi cho mỗi lần làm'
    )
    shuffle_answers = models.BooleanField(
        default=False,
        verbose_name='Trộn đáp án',
        help_text='Trộn ngẫu nhiên thứ tự đáp án cho mỗi câu hỏi'
    )
    show_result = models.BooleanField(
        default=True,
        verbose_name='Hiển thị kết quả',
        help_text='Cho phép học viên xem kết quả sau khi nộp bài'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assignments'
        verbose_name = 'Bài tập'
        verbose_name_plural = 'Bài tập'
        ordering = ['lesson', 'start_at']
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"
    
    @property
    def is_open(self) -> bool:
        """Kiểm tra bài tập có đang mở không"""
        from django.utils import timezone
        now = timezone.now()
        return self.start_at <= now <= self.end_at
    
    @property
    def is_upcoming(self) -> bool:
        """Kiểm tra bài tập chưa mở"""
        from django.utils import timezone
        return timezone.now() < self.start_at
    
    @property
    def is_closed(self) -> bool:
        """Kiểm tra bài tập đã đóng"""
        from django.utils import timezone
        return timezone.now() > self.end_at
    
    @property
    def question_count(self) -> int:
        """Số lượng câu hỏi"""
        return self.questions.count()


class QuestionModel(models.Model):
    """
    Question - Câu hỏi trắc nghiệm
    
    Mỗi câu hỏi thuộc về một Assignment (bài tập).
    Hỗ trợ 4 đáp án A, B, C, D.
    """
    
    class AnswerChoice(models.TextChoices):
        A = 'A', 'A'
        B = 'B', 'B'
        C = 'C', 'C'
        D = 'D', 'D'

    assignment = models.ForeignKey(
        AssignmentModel,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Bài tập'
    )
    text = models.TextField(verbose_name='Nội dung câu hỏi')
    option_a = models.CharField(max_length=500, verbose_name='Đáp án A')
    option_b = models.CharField(max_length=500, verbose_name='Đáp án B')
    option_c = models.CharField(max_length=500, verbose_name='Đáp án C')
    option_d = models.CharField(max_length=500, verbose_name='Đáp án D')
    correct_answer = models.CharField(
        max_length=1,
        choices=AnswerChoice.choices,
        verbose_name='Đáp án đúng'
    )
    explanation = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Giải thích',
        help_text='Giải thích đáp án đúng (hiển thị sau khi nộp bài)'
    )
    points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0)],
        verbose_name='Điểm',
        help_text='Điểm cho câu hỏi này'
    )
    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Thứ tự'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        verbose_name = 'Câu hỏi'
        verbose_name_plural = 'Câu hỏi'
        ordering = ['assignment', 'order']
    
    def __str__(self):
        text_preview = self.text[:50] + '...' if len(self.text) > 50 else self.text
        return f"Q{self.order}: {text_preview}"
    
    def save(self, *args, **kwargs):
        """Xử lý order khi save"""
        from ..utils.order_manager import handle_order_on_save
        handle_order_on_save(self, 'assignment', 'order')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Sắp xếp lại order khi xóa"""
        from ..utils.order_manager import handle_order_on_delete
        handle_order_on_delete(self, 'assignment', 'order')
        super().delete(*args, **kwargs)
    
    @property
    def correct_answer_text(self) -> str:
        """Lấy nội dung đáp án đúng"""
        answer_map = {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }
        return answer_map.get(self.correct_answer, '')


class AttemptModel(models.Model):
    """
    Attempt - Lần làm bài của học viên
    
    Trạng thái:
    - IN_PROGRESS: Đang làm
    - SUBMITTED: Đã nộp
    - GRADED: Đã chấm điểm
    """
    
    class AttemptStatus(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'Đang làm'
        SUBMITTED = 'SUBMITTED', 'Đã nộp'
        GRADED = 'GRADED', 'Đã chấm điểm'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Học viên'
    )
    assignment = models.ForeignKey(
        AssignmentModel,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Bài tập'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Bắt đầu lúc')
    submitted_at = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name='Nộp lúc'
    )
    # File nộp bài (cho bài tập FILE_UPLOAD)
    submitted_file = models.FileField(
        upload_to='submissions/',
        blank=True,
        null=True,
        validators=[SubmissionFileValidator()],
        verbose_name='File nộp bài',
        help_text='File nộp bài: PDF, DOC, DOCX, PPT, XLS, ZIP, RAR, JPG, PNG, PY, JAVA, etc. (tối đa 50MB)'
    )
    # Nội dung text (cho bài tập dạng viết)
    submitted_text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Nội dung nộp'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Điểm'
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name='Nhận xét của giảng viên'
    )
    status = models.CharField(
        max_length=20,
        choices=AttemptStatus.choices,
        default=AttemptStatus.IN_PROGRESS,
        verbose_name='Trạng thái'
    )
    
    class Meta:
        db_table = 'attempts'
        verbose_name = 'Lần làm bài'
        verbose_name_plural = 'Lần làm bài'
        ordering = ['-started_at']
    
    def __str__(self):
        user_name = self.user.full_name if self.user else 'Unknown'
        assignment_title = self.assignment.title if self.assignment else 'Unknown'
        return f"{user_name} - {assignment_title} ({self.get_status_display()})"
    
    @property
    def correct_count(self) -> int:
        """Số câu trả lời đúng"""
        return self.details.filter(is_correct=True).count()
    
    @property
    def total_questions(self) -> int:
        """Tổng số câu hỏi đã trả lời"""
        return self.details.count()
    
    def calculate_score(self) -> float:
        """
        Tính điểm dựa trên câu trả lời
        
        Công thức: (earned_points / total_points) * max_score
        
        Ví dụ: 4 câu hỏi (1đ, 1đ, 1đ, 2đ) = tổng 5 điểm
        - Làm đúng câu 4 (2đ): 2/5 * 100 = 40 điểm
        - Làm đúng câu 1,2,3 (3đ): 3/5 * 100 = 60 điểm
        """
        if self.assignment.type != 'QUIZ':
            return 0
        
        # Tổng điểm tất cả câu hỏi của assignment (không chỉ câu đã trả lời)
        from django.db.models import Sum
        total_points_result = self.assignment.questions.aggregate(total=Sum('points'))
        total_points = float(total_points_result['total'] or 0)
        
        if total_points == 0:
            return 0
        
        # Điểm đạt được từ các câu trả lời đúng
        earned_points = 0
        for detail in self.details.select_related('question'):
            if detail.is_correct:
                earned_points += float(detail.question.points)
        
        # Quy về max_score
        return (earned_points / total_points) * float(self.assignment.max_score)
    
    def save(self, *args, **kwargs):
        """Xóa file cũ khi thay đổi submitted_file"""
        import os
        
        # Xóa file cũ nếu thay đổi file (chỉ khi update, không phải tạo mới)
        if not self._state.adding:  # Nếu đây là update, không phải tạo mới
            try:
                old_instance = AttemptModel.objects.get(pk=self.pk)
                
                # Xóa submitted_file cũ nếu thay đổi
                if old_instance.submitted_file:
                    # Kiểm tra xem file có thay đổi không
                    file_changed = False
                    if not self.submitted_file:
                        # File bị xóa
                        file_changed = True
                    elif hasattr(self.submitted_file, 'name') and old_instance.submitted_file.name != self.submitted_file.name:
                        # File đã thay đổi
                        file_changed = True
                    
                    if file_changed:
                        try:
                            if os.path.isfile(old_instance.submitted_file.path):
                                os.remove(old_instance.submitted_file.path)
                        except Exception:
                            pass  # Bỏ qua lỗi khi xóa file
            except AttemptModel.DoesNotExist:
                pass  # Record mới, không có file cũ
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Xóa file khi xóa record"""
        import os
        
        if self.submitted_file:
            if os.path.isfile(self.submitted_file.path):
                try:
                    os.remove(self.submitted_file.path)
                except:
                    pass
        
        super().delete(*args, **kwargs)


class AttemptDetailModel(models.Model):
    """
    AttemptDetail - Chi tiết câu trả lời của mỗi câu hỏi
    
    Lưu lại đáp án mà học viên chọn cho từng câu hỏi.
    """
    
    class AnswerChoice(models.TextChoices):
        A = 'A', 'A'
        B = 'B', 'B'
        C = 'C', 'C'
        D = 'D', 'D'

    attempt = models.ForeignKey(
        AttemptModel,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='Lần làm bài'
    )
    question = models.ForeignKey(
        QuestionModel,
        on_delete=models.CASCADE,
        related_name='attempt_details',
        verbose_name='Câu hỏi'
    )
    chosen_answer = models.CharField(
        max_length=1,
        choices=AnswerChoice.choices,
        blank=True,
        null=True,
        verbose_name='Đáp án đã chọn'
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name='Đúng/Sai'
    )
    
    class Meta:
        db_table = 'attempt_details'
        verbose_name = 'Chi tiết câu trả lời'
        verbose_name_plural = 'Chi tiết câu trả lời'
        unique_together = [['attempt', 'question']]
        ordering = ['attempt', 'question__order']
    
    def __str__(self):
        status = '✓' if self.is_correct else '✗'
        return f"{self.attempt.user.username} - Q{self.question.order} ({status})"
    
    def save(self, *args, **kwargs):
        """Tự động kiểm tra đáp án đúng/sai khi lưu"""
        if self.chosen_answer:
            self.is_correct = (self.chosen_answer == self.question.correct_answer)
        else:
            self.is_correct = False
        super().save(*args, **kwargs)
