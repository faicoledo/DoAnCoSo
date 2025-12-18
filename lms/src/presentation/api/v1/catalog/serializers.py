"""
Catalog Serializers

Serializers cho các API nội dung khóa học.
"""
from rest_framework import serializers


# ==================== MY COURSES ====================

class MyCourseSerializer(serializers.Serializer):
    """
    Serializer cho danh sách khóa học của user
    GET /api/v1/catalog/my-courses/
    """
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    course_description = serializers.CharField(allow_blank=True, required=False)
    subject_id = serializers.IntegerField()
    subject_title = serializers.CharField()
    status = serializers.CharField(help_text="UPCOMING, ONGOING, COMPLETED")
    status_display = serializers.CharField()
    role_in_course = serializers.CharField(help_text="STUDENT, TEACHER, TA")
    role_display = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    joined_at = serializers.DateTimeField()


# ==================== COURSE DETAIL ====================

class LessonBriefSerializer(serializers.Serializer):
    """Serializer tóm tắt bài học"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    order = serializers.IntegerField()


class ModuleWithLessonsSerializer(serializers.Serializer):
    """Serializer module kèm danh sách bài học"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    order = serializers.IntegerField()
    lessons = LessonBriefSerializer(many=True)
    lessons_count = serializers.IntegerField()


class SubjectBriefSerializer(serializers.Serializer):
    """Serializer tóm tắt môn học"""
    id = serializers.IntegerField()
    title = serializers.CharField()


class ResourceBriefSerializer(serializers.Serializer):
    """Serializer tóm tắt tài liệu"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    type = serializers.CharField()


class AssignmentBriefInLessonSerializer(serializers.Serializer):
    """Serializer tóm tắt bài tập trong bài học"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    type = serializers.CharField()


class LessonWithContentSerializer(serializers.Serializer):
    """Serializer bài học kèm tài liệu và bài tập"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    order = serializers.IntegerField()
    resources = ResourceBriefSerializer(many=True, required=False)
    assignments = AssignmentBriefInLessonSerializer(many=True, required=False)


class ModuleWithFullLessonsSerializer(serializers.Serializer):
    """Serializer module kèm danh sách bài học đầy đủ"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    order = serializers.IntegerField()
    lessons = LessonWithContentSerializer(many=True)
    lessons_count = serializers.IntegerField()


class CourseDetailSerializer(serializers.Serializer):
    """
    Serializer chi tiết khóa học
    GET /api/v1/catalog/courses/{course_id}/
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.CharField()
    status_display = serializers.CharField()
    start_date = serializers.DateField(allow_null=True)
    end_date = serializers.DateField(allow_null=True)
    subject = SubjectBriefSerializer(allow_null=True)
    modules = ModuleWithFullLessonsSerializer(many=True)
    total_modules = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    # Thông tin enrollment của user hiện tại
    my_role = serializers.CharField(required=False)
    my_role_display = serializers.CharField(required=False)


# ==================== LESSON DETAIL ====================

class ResourceSerializer(serializers.Serializer):
    """
    Serializer cho tài liệu
    
    Loại tài liệu:
    - DOCUMENT: Tài liệu (PDF, DOC, etc.) - có document_url
    - VIDEO: Video - có video_url (từ file upload hoặc URL nhập)
    - LINK: Liên kết - có link_url
    - TEXT: Văn bản - có text_content
    """
    id = serializers.IntegerField()
    type = serializers.CharField(help_text="DOCUMENT, VIDEO, LINK, TEXT")
    type_display = serializers.CharField()
    title = serializers.CharField()
    
    # URL tùy theo loại
    document_url = serializers.CharField(allow_null=True, required=False, help_text="URL tài liệu (DOCUMENT)")
    video_url = serializers.CharField(allow_null=True, required=False, help_text="URL video (VIDEO)")
    link_url = serializers.CharField(allow_null=True, required=False, help_text="URL liên kết (LINK)")
    text_content = serializers.CharField(allow_null=True, allow_blank=True, required=False, help_text="Nội dung văn bản (TEXT)")
    
    # Metadata
    file_size = serializers.IntegerField(allow_null=True, required=False)
    file_size_display = serializers.CharField(required=False)
    duration = serializers.IntegerField(allow_null=True, required=False, help_text="Thời lượng video (giây)")
    duration_display = serializers.CharField(required=False)
    is_uploaded = serializers.BooleanField(required=False, help_text="Có phải file upload không")
    order = serializers.IntegerField()


class AssignmentBriefSerializer(serializers.Serializer):
    """Serializer tóm tắt bài tập"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    type = serializers.CharField(help_text="QUIZ, FILE_UPLOAD")
    type_display = serializers.CharField()
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    time_limit = serializers.IntegerField(allow_null=True, help_text="Thời gian làm bài (phút)")
    attempts_allowed = serializers.IntegerField()
    is_available = serializers.BooleanField(help_text="Bài tập có đang mở không")


class ModuleBriefSerializer(serializers.Serializer):
    """Serializer tóm tắt module"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    order = serializers.IntegerField()


class CourseBriefSerializer(serializers.Serializer):
    """Serializer tóm tắt khóa học"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    status = serializers.CharField()
    status_display = serializers.CharField()


class LessonDetailSerializer(serializers.Serializer):
    """
    Serializer chi tiết bài học
    GET /api/v1/catalog/lessons/{lesson_id}/
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField(allow_null=True, allow_blank=True)
    order = serializers.IntegerField()
    module = ModuleBriefSerializer()
    course = CourseBriefSerializer()
    resources = ResourceSerializer(many=True)
    assignments = AssignmentBriefSerializer(many=True)
    resources_count = serializers.IntegerField()
    assignments_count = serializers.IntegerField()
    # Navigation
    prev_lesson = LessonBriefSerializer(allow_null=True, required=False)
    next_lesson = LessonBriefSerializer(allow_null=True, required=False)

