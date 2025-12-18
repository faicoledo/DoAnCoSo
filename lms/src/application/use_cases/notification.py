"""
Notification Use Cases

Các use case cho chức năng Notification:
- CreateNotificationUseCase: Tạo thông báo cho một hoặc nhiều user
- MarkNotificationAsReadUseCase: Đánh dấu thông báo đã đọc
- ListUserNotificationsUseCase: Lấy danh sách thông báo của user
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from ...infrastructure.persistence.models.communication import NotificationModel
from ...infrastructure.persistence.models.enrollment import EnrollmentModel
from ...infrastructure.persistence.models.course import LessonModel, CourseModel
from ...infrastructure.persistence.models.assessment import AssignmentModel


# ==================== DTOs ====================

@dataclass
class CreateNotificationInput:
    """Input DTO cho CreateNotificationUseCase"""
    user_ids: List[int]  # Danh sách user IDs để gửi thông báo
    title: str
    message: str
    type: str  # NotificationType
    related_object_type: Optional[str] = None
    related_object_id: Optional[int] = None


@dataclass
class NotificationDTO:
    """Output DTO cho Notification"""
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    related_object_type: Optional[str]
    related_object_id: Optional[int]
    created_at: datetime
    
    @classmethod
    def from_model(cls, notification: NotificationModel) -> 'NotificationDTO':
        return cls(
            id=notification.id,
            title=notification.title,
            message=notification.message,
            type=notification.type,
            is_read=notification.is_read,
            related_object_type=notification.related_object_type,
            related_object_id=notification.related_object_id,
            created_at=notification.created_at,
        )


@dataclass
class ListNotificationsInput:
    """Input DTO cho ListUserNotificationsUseCase"""
    user_id: int
    is_read: Optional[bool] = None  # None = tất cả, True = chỉ đã đọc, False = chỉ chưa đọc
    limit: Optional[int] = None
    offset: int = 0


# ==================== USE CASES ====================

class CreateNotificationUseCase:
    """
    Tạo thông báo cho một hoặc nhiều user
    
    Sử dụng để gửi thông báo tự động hoặc thủ công.
    """
    
    @transaction.atomic
    def execute(self, input_dto: CreateNotificationInput) -> List[NotificationModel]:
        """
        Tạo thông báo cho tất cả user trong user_ids
        
        Returns:
            List các NotificationModel đã tạo
        """
        notifications = []
        
        for user_id in input_dto.user_ids:
            notification = NotificationModel.objects.create(
                user_id=user_id,
                title=input_dto.title,
                message=input_dto.message,
                type=input_dto.type,
                related_object_type=input_dto.related_object_type,
                related_object_id=input_dto.related_object_id,
            )
            notifications.append(notification)
        
        return notifications


class MarkNotificationAsReadUseCase:
    """
    Đánh dấu thông báo đã đọc
    """
    
    def execute(self, notification_id: int, user_id: int) -> NotificationModel:
        """
        Đánh dấu thông báo đã đọc
        
        Chỉ user sở hữu thông báo mới được đánh dấu.
        """
        try:
            notification = NotificationModel.objects.get(
                pk=notification_id,
                user_id=user_id
            )
        except NotificationModel.DoesNotExist:
            raise ValueError(f"Thông báo {notification_id} không tồn tại hoặc không thuộc về user {user_id}")
        
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        
        return notification


class ListUserNotificationsUseCase:
    """
    Lấy danh sách thông báo của user
    """
    
    def execute(self, input_dto: ListNotificationsInput) -> List[NotificationDTO]:
        """
        Lấy danh sách thông báo của user
        
        Returns:
            List các NotificationDTO
        """
        queryset = NotificationModel.objects.filter(user_id=input_dto.user_id)
        
        # Lọc theo is_read nếu có
        if input_dto.is_read is not None:
            queryset = queryset.filter(is_read=input_dto.is_read)
        
        # Sắp xếp theo thời gian tạo (mới nhất trước)
        queryset = queryset.order_by('-created_at')
        
        # Pagination
        if input_dto.offset:
            queryset = queryset[input_dto.offset:]
        if input_dto.limit:
            queryset = queryset[:input_dto.limit]
        
        return [NotificationDTO.from_model(n) for n in queryset]


# ==================== HELPER FUNCTIONS ====================

def notify_students_on_new_lesson(lesson_id: int, course_id: int):
    """
    Gửi thông báo cho tất cả học viên trong khóa học khi có bài học mới
    
    Args:
        lesson_id: ID của lesson mới
        course_id: ID của course
    """
    # Lấy tất cả học viên đã enroll trong khóa học
    enrollments = EnrollmentModel.objects.filter(
        course_id=course_id,
        role_in_course='STUDENT'
    ).select_related('user')
    
    if not enrollments.exists():
        return
    
    try:
        lesson = LessonModel.objects.get(pk=lesson_id)
        course = CourseModel.objects.get(pk=course_id)
    except (LessonModel.DoesNotExist, CourseModel.DoesNotExist):
        return
    
    user_ids = [enrollment.user_id for enrollment in enrollments]
    
    use_case = CreateNotificationUseCase()
    use_case.execute(CreateNotificationInput(
        user_ids=user_ids,
        title=f"Bài học mới: {lesson.title}",
        message=f"Khóa học '{course.title}' có bài học mới: {lesson.title}",
        type=NotificationModel.NotificationType.LESSON_CREATED,
        related_object_type='lesson',
        related_object_id=lesson_id,
    ))


def notify_students_on_new_assignment(assignment_id: int, course_id: int):
    """
    Gửi thông báo cho tất cả học viên trong khóa học khi có bài tập mới
    
    Args:
        assignment_id: ID của assignment mới
        course_id: ID của course
    """
    # Lấy tất cả học viên đã enroll trong khóa học
    enrollments = EnrollmentModel.objects.filter(
        course_id=course_id,
        role_in_course='STUDENT'
    ).select_related('user')
    
    if not enrollments.exists():
        return
    
    try:
        assignment = AssignmentModel.objects.select_related('lesson').get(pk=assignment_id)
        course = CourseModel.objects.get(pk=course_id)
    except (AssignmentModel.DoesNotExist, CourseModel.DoesNotExist):
        return
    
    user_ids = [enrollment.user_id for enrollment in enrollments]
    
    use_case = CreateNotificationUseCase()
    use_case.execute(CreateNotificationInput(
        user_ids=user_ids,
        title=f"Bài tập mới: {assignment.title}",
        message=f"Khóa học '{course.title}' có bài tập mới: {assignment.title}",
        type=NotificationModel.NotificationType.ASSIGNMENT_CREATED,
        related_object_type='assignment',
        related_object_id=assignment_id,
    ))


def notify_student_on_assignment_graded(attempt_id: int, user_id: int, score: float, max_score: float):
    """
    Gửi thông báo cho học viên khi bài tập được chấm điểm
    
    Args:
        attempt_id: ID của attempt
        user_id: ID của học viên
        score: Điểm đạt được
        max_score: Điểm tối đa
    """
    try:
        from ...infrastructure.persistence.models.assessment import AttemptModel
        attempt = AttemptModel.objects.select_related('assignment').get(pk=attempt_id)
        assignment = attempt.assignment
    except AttemptModel.DoesNotExist:
        return
    
    use_case = CreateNotificationUseCase()
    use_case.execute(CreateNotificationInput(
        user_ids=[user_id],
        title=f"Kết quả bài tập: {assignment.title}",
        message=f"Bài tập '{assignment.title}' đã được chấm điểm. Điểm số: {score:.2f}/{max_score:.2f}",
        type=NotificationModel.NotificationType.ASSIGNMENT_GRADED,
        related_object_type='attempt',
        related_object_id=attempt_id,
    ))


def notify_students_on_assignment_deadline(assignment_id: int, course_id: int):
    """
    Gửi thông báo cho học viên khi bài tập sắp đến hạn (trước 1 giờ)
    
    Args:
        assignment_id: ID của assignment
        course_id: ID của course
    """
    # Lấy tất cả học viên đã enroll trong khóa học
    enrollments = EnrollmentModel.objects.filter(
        course_id=course_id,
        role_in_course='STUDENT'
    ).select_related('user')
    
    if not enrollments.exists():
        return
    
    try:
        assignment = AssignmentModel.objects.select_related('lesson__module__course').get(pk=assignment_id)
        course = assignment.lesson.module.course
    except AssignmentModel.DoesNotExist:
        return
    
    user_ids = [enrollment.user_id for enrollment in enrollments]
    
    use_case = CreateNotificationUseCase()
    use_case.execute(CreateNotificationInput(
        user_ids=user_ids,
        title=f"Bài tập sắp đến hạn: {assignment.title}",
        message=f"Bài tập '{assignment.title}' trong khóa học '{course.title}' sẽ đến hạn trong 1 giờ nữa.",
        type=NotificationModel.NotificationType.ASSIGNMENT_DEADLINE,
        related_object_type='assignment',
        related_object_id=assignment_id,
    ))



