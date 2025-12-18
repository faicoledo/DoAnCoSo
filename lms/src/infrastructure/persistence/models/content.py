"""
Content Django ORM Models

Quản lý tài liệu học tập:
- Tài liệu (PDF, DOC, etc.): Upload từ máy tính
- Video: Có thể upload từ máy HOẶC dùng URL
- Link: URL bên ngoài
- Text: Nội dung văn bản
"""
import os
from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from ..validators import DocumentFileValidator, VideoFileValidator


def resource_file_path(instance, filename):
    """
    Tạo đường dẫn lưu file tài liệu.
    Format: resources/course_{course_id}/lesson_{lesson_id}/{filename}
    """
    lesson = instance.lesson
    course_id = lesson.module.course_id
    lesson_id = lesson.id
    
    # Tạo tên file an toàn
    base, ext = os.path.splitext(filename)
    safe_filename = f"{base}_{instance.id or 'new'}{ext}"
    
    return f'resources/course_{course_id}/lesson_{lesson_id}/{safe_filename}'


def video_file_path(instance, filename):
    """
    Tạo đường dẫn lưu file video.
    Format: videos/course_{course_id}/lesson_{lesson_id}/{filename}
    """
    lesson = instance.lesson
    course_id = lesson.module.course_id
    lesson_id = lesson.id
    
    base, ext = os.path.splitext(filename)
    safe_filename = f"{base}_{instance.id or 'new'}{ext}"
    
    return f'videos/course_{course_id}/lesson_{lesson_id}/{safe_filename}'


class ResourceModel(models.Model):
    """
    Resource - Tài liệu học tập
    
    Các loại tài liệu:
    - DOCUMENT: Tài liệu (PDF, DOC, PPT, etc.) - Upload từ máy
    - VIDEO: Video - Upload từ máy HOẶC URL
    - LINK: Liên kết bên ngoài
    - TEXT: Nội dung văn bản
    """
    
    class ResourceType(models.TextChoices):
        DOCUMENT = 'DOCUMENT', 'Tài liệu'
        VIDEO = 'VIDEO', 'Video'
        LINK = 'LINK', 'Liên kết'
        TEXT = 'TEXT', 'Văn bản'
    
    class VideoSource(models.TextChoices):
        FILE = 'FILE', 'Upload file'
        URL = 'URL', 'URL video'
    
    # Allowed file extensions
    DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'zip', 'rar']
    VIDEO_EXTENSIONS = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'm4v']

    lesson = models.ForeignKey(
        'LessonModel',
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='Bài học'
    )
    type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        verbose_name='Loại tài liệu'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Tiêu đề'
    )
    
    # === File upload cho tài liệu ===
    document_file = models.FileField(
        upload_to=resource_file_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=DOCUMENT_EXTENSIONS),
            DocumentFileValidator(),
        ],
        verbose_name='File tài liệu',
        help_text='Upload tài liệu: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT, ZIP, RAR (tối đa 20MB)'
    )
    
    # === Video: chọn nguồn (file hoặc URL) ===
    video_source = models.CharField(
        max_length=10,
        choices=VideoSource.choices,
        blank=True,
        null=True,
        verbose_name='Nguồn video',
        help_text='Chọn upload file hoặc nhập URL'
    )
    video_file = models.FileField(
        upload_to=video_file_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=VIDEO_EXTENSIONS),
            VideoFileValidator(),
        ],
        verbose_name='File video',
        help_text='Upload video: MP4, WEBM, OGG, MOV, AVI, MKV, WMV, FLV, M4V (tối đa 500MB)'
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL video',
        help_text='Nhập URL video (YouTube, Vimeo, etc.)'
    )
    
    # === Link bên ngoài ===
    external_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL liên kết',
        help_text='URL liên kết bên ngoài'
    )
    
    # === Nội dung text ===
    text_content = models.TextField(
        blank=True,
        null=True,
        verbose_name='Nội dung văn bản',
        help_text='Nội dung văn bản hiển thị trực tiếp'
    )
    
    # === Metadata ===
    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name='Thời lượng (giây)',
        help_text='Tự động tính từ video file hoặc URL (chỉ đọc)'
    )
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Kích thước file (bytes)',
        help_text='Tự động tính khi upload'
    )
    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Thứ tự'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resources'
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu'
        ordering = ['lesson', 'order']
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title} ({self.get_type_display()})"
    
    def clean(self):
        """Validate dữ liệu theo loại tài liệu"""
        errors = {}
        
        if self.type == self.ResourceType.DOCUMENT:
            # Chỉ cho phép document_file, không cho các field khác
            if not self.document_file:
                errors['document_file'] = 'Vui lòng upload file tài liệu.'
            elif self.document_file:
                # Validate extension và size
                try:
                    DocumentFileValidator()(self.document_file)
                except ValidationError as e:
                    errors['document_file'] = str(e)
            # Xóa các field không liên quan
            self.video_file = None
            self.video_url = None
            self.video_source = None
            self.external_url = None
            self.text_content = None
            self.duration = None
        
        elif self.type == self.ResourceType.VIDEO:
            # Phải chọn video_source
            if not self.video_source:
                errors['video_source'] = 'Vui lòng chọn nguồn video (Upload file hoặc URL).'
            elif self.video_source == self.VideoSource.FILE:
                if not self.video_file:
                    errors['video_file'] = 'Vui lòng upload file video.'
                elif self.video_file:
                    # Validate extension và size
                    try:
                        VideoFileValidator()(self.video_file)
                    except ValidationError as e:
                        errors['video_file'] = str(e)
                # Xóa video_url
                self.video_url = None
            elif self.video_source == self.VideoSource.URL:
                if not self.video_url:
                    errors['video_url'] = 'Vui lòng nhập URL video.'
                # Xóa video_file
                self.video_file = None
            # Xóa các field không liên quan
            self.document_file = None
            self.external_url = None
            self.text_content = None
        
        elif self.type == self.ResourceType.LINK:
            if not self.external_url:
                errors['external_url'] = 'Vui lòng nhập URL liên kết.'
            # Xóa các field không liên quan
            self.document_file = None
            self.video_file = None
            self.video_url = None
            self.video_source = None
            self.text_content = None
            self.duration = None
        
        elif self.type == self.ResourceType.TEXT:
            if not self.text_content:
                errors['text_content'] = 'Vui lòng nhập nội dung văn bản.'
            # Xóa các field không liên quan
            self.document_file = None
            self.video_file = None
            self.video_url = None
            self.video_source = None
            self.external_url = None
            self.duration = None
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        # Xử lý order trước
        from ..utils.order_manager import handle_order_on_save
        handle_order_on_save(self, 'lesson', 'order')
        
        # Xóa file cũ nếu thay đổi file (chỉ khi update, không phải tạo mới)
        if not self._state.adding:  # Nếu đây là update, không phải tạo mới
            try:
                old_instance = ResourceModel.objects.get(pk=self.pk)
                
                # Xóa document_file cũ nếu thay đổi
                if old_instance.document_file:
                    # Kiểm tra xem file có thay đổi không
                    file_changed = False
                    if not self.document_file:
                        # File bị xóa
                        file_changed = True
                    elif hasattr(self.document_file, 'name') and old_instance.document_file.name != self.document_file.name:
                        # File đã thay đổi
                        file_changed = True
                    
                    if file_changed:
                        try:
                            if os.path.isfile(old_instance.document_file.path):
                                os.remove(old_instance.document_file.path)
                        except Exception:
                            pass  # Bỏ qua lỗi khi xóa file
                
                # Xóa video_file cũ nếu thay đổi
                if old_instance.video_file:
                    # Kiểm tra xem file có thay đổi không
                    file_changed = False
                    if not self.video_file:
                        # File bị xóa
                        file_changed = True
                    elif hasattr(self.video_file, 'name') and old_instance.video_file.name != self.video_file.name:
                        # File đã thay đổi
                        file_changed = True
                    
                    if file_changed:
                        try:
                            if os.path.isfile(old_instance.video_file.path):
                                os.remove(old_instance.video_file.path)
                        except Exception:
                            pass  # Bỏ qua lỗi khi xóa file
            except ResourceModel.DoesNotExist:
                pass  # Record mới, không có file cũ
        
        # Tự động tính file_size
        if self.document_file:
            try:
                self.file_size = self.document_file.size
            except:
                self.file_size = None
        elif self.video_file:
            try:
                self.file_size = self.video_file.size
            except:
                self.file_size = None
        else:
            # Nếu không có file, set file_size = None
            self.file_size = None
        
        # Tự động tính duration cho video
        if self.type == self.ResourceType.VIDEO:
            from src.infrastructure.services.video_duration import get_video_duration_from_file, get_video_duration_from_url
            
            # Chỉ tính nếu chưa có duration hoặc file/URL thay đổi
            if self.video_source == self.VideoSource.FILE and self.video_file:
                try:
                    # Reset file pointer để đọc lại
                    self.video_file.seek(0)
                    duration = get_video_duration_from_file(self.video_file)
                    if duration:
                        self.duration = duration
                    else:
                        self.duration = None  # Không tính được thì bỏ
                except:
                    self.duration = None
            elif self.video_source == self.VideoSource.URL and self.video_url:
                try:
                    duration = get_video_duration_from_url(self.video_url)
                    if duration:
                        self.duration = duration
                    else:
                        self.duration = None  # Không tính được thì bỏ
                except:
                    self.duration = None
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Xóa file khi xóa record"""
        # Sắp xếp lại order trước khi xóa
        from ..utils.order_manager import handle_order_on_delete
        handle_order_on_delete(self, 'lesson', 'order')
        
        # Xóa document file
        if self.document_file:
            try:
                if os.path.isfile(self.document_file.path):
                    os.remove(self.document_file.path)
            except Exception:
                pass
        
        # Xóa video file
        if self.video_file:
            try:
                if os.path.isfile(self.video_file.path):
                    os.remove(self.video_file.path)
            except Exception:
                pass
        
        super().delete(*args, **kwargs)
    
    # === Helper properties ===
    
    @property
    def file_url(self):
        """Trả về URL của file (để tương thích với code cũ)"""
        if self.type == self.ResourceType.DOCUMENT and self.document_file:
            return self.document_file.url
        elif self.type == self.ResourceType.VIDEO:
            if self.video_file:
                return self.video_file.url
            return self.video_url
        elif self.type == self.ResourceType.LINK:
            return self.external_url
        return None
    
    @property
    def is_uploaded(self) -> bool:
        """Kiểm tra có phải file upload không"""
        return bool(self.document_file or self.video_file)
    
    @property
    def file_size_display(self) -> str:
        """Hiển thị kích thước file dạng đọc được"""
        if not self.file_size:
            return ''
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    @property
    def duration_display(self) -> str:
        """Hiển thị thời lượng dạng MM:SS"""
        if not self.duration:
            return ''
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
