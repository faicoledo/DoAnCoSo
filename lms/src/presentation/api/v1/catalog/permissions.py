"""
Custom Permissions for Catalog API

Kiểm tra quyền truy cập dựa trên Enrollment.
"""
from rest_framework import permissions
from .....infrastructure.persistence.models.enrollment import EnrollmentModel


class IsEnrolledInCourse(permissions.BasePermission):
    """
    Kiểm tra user đã enroll vào khóa học hay chưa.
    Dùng cho CourseDetailView.
    """
    message = "Bạn chưa đăng ký khóa học này."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        course_id = view.kwargs.get('course_id') or view.kwargs.get('pk')
        if not course_id:
            return False
        
        return EnrollmentModel.objects.filter(
            user=request.user,
            course_id=course_id
        ).exists()


class IsEnrolledInLessonCourse(permissions.BasePermission):
    """
    Kiểm tra user đã enroll vào khóa học chứa lesson hay chưa.
    Và khóa học phải đang diễn ra (ONGOING) mới được truy cập bài học.
    Dùng cho LessonDetailView.
    """
    message = "Bạn chưa đăng ký khóa học chứa bài học này hoặc khóa học chưa bắt đầu."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        lesson_id = view.kwargs.get('lesson_id') or view.kwargs.get('pk')
        if not lesson_id:
            return False
        
        # Import here to avoid circular imports
        from .....infrastructure.persistence.models.course import LessonModel
        
        try:
            lesson = LessonModel.objects.select_related(
                'module__course'
            ).get(pk=lesson_id)
            course = lesson.module.course
        except LessonModel.DoesNotExist:
            return False
        
        # Kiểm tra khóa học đang diễn ra (ONGOING)
        if course.computed_status != 'ONGOING':
            self.message = "Khóa học chưa bắt đầu hoặc đã kết thúc. Bạn không thể truy cập bài học."
            return False
        
        return EnrollmentModel.objects.filter(
            user=request.user,
            course_id=course.id
        ).exists()

