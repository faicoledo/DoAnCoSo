"""
File Upload Validators

Custom validators để kiểm tra định dạng và kích thước file.
"""
from django.core.exceptions import ValidationError
from django.conf import settings


def validate_file_extension(file, allowed_extensions):
    """
    Validate file extension
    
    Args:
        file: File object
        allowed_extensions: List of allowed extensions (lowercase, without dot)
    
    Raises:
        ValidationError: Nếu extension không hợp lệ
    """
    if not file:
        return
    
    # Lấy extension
    filename = file.name
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    
    if not ext:
        raise ValidationError(
            f'File không có phần mở rộng. Định dạng được phép: {", ".join(allowed_extensions).upper()}'
        )
    
    if ext not in [e.lower() for e in allowed_extensions]:
        raise ValidationError(
            f'Định dạng file "{ext.upper()}" không được phép. '
            f'Định dạng được phép: {", ".join(allowed_extensions).upper()}'
        )


def validate_file_size(file, max_size_mb):
    """
    Validate file size
    
    Args:
        file: File object
        max_size_mb: Maximum size in MB
    
    Raises:
        ValidationError: Nếu file quá lớn
    """
    if not file:
        return
    
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file.size > max_size_bytes:
        raise ValidationError(
            f'File quá lớn ({file.size / 1024 / 1024:.1f} MB). '
            f'Kích thước tối đa: {max_size_mb} MB'
        )


class DocumentFileValidator:
    """
    Validator cho file tài liệu (PDF, DOC, etc.)
    """
    ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'zip', 'rar']
    MAX_SIZE_MB = getattr(settings, 'MAX_DOCUMENT_SIZE_MB', 20)  # 20MB mặc định
    
    def __call__(self, value):
        if not value:
            return
        
        validate_file_extension(value, self.ALLOWED_EXTENSIONS)
        validate_file_size(value, self.MAX_SIZE_MB)
    
    def deconstruct(self):
        """Cho phép Django serialize validator trong migrations"""
        return (
            'src.infrastructure.persistence.validators.DocumentFileValidator',
            [],
            {}
        )


class VideoFileValidator:
    """
    Validator cho file video
    """
    ALLOWED_EXTENSIONS = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'm4v']
    MAX_SIZE_MB = getattr(settings, 'MAX_VIDEO_SIZE_MB', 500)  # 500MB mặc định
    
    def __call__(self, value):
        if not value:
            return
        
        validate_file_extension(value, self.ALLOWED_EXTENSIONS)
        validate_file_size(value, self.MAX_SIZE_MB)
    
    def deconstruct(self):
        """Cho phép Django serialize validator trong migrations"""
        return (
            'src.infrastructure.persistence.validators.VideoFileValidator',
            [],
            {}
        )


class SubmissionFileValidator:
    """
    Validator cho file nộp bài (Assignment FILE_UPLOAD)
    """
    ALLOWED_EXTENSIONS = [
        # Documents
        'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt',
        # Archives
        'zip', 'rar', '7z',
        # Images (nếu cần)
        'jpg', 'jpeg', 'png', 'gif',
        # Code files (nếu cần)
        'py', 'java', 'cpp', 'c', 'js', 'html', 'css',
    ]
    MAX_SIZE_MB = 50  # 50MB cho file nộp bài
    
    def __call__(self, value):
        if not value:
            return
        
        validate_file_extension(value, self.ALLOWED_EXTENSIONS)
        validate_file_size(value, self.MAX_SIZE_MB)
    
    def deconstruct(self):
        """Cho phép Django serialize validator trong migrations"""
        return (
            'src.infrastructure.persistence.validators.SubmissionFileValidator',
            [],
            {}
        )

