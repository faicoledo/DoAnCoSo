"""
Course Domain Exceptions
"""
from .base import DomainException, EntityNotFoundException


class CourseNotFoundException(EntityNotFoundException):
    """Raised when a course is not found"""
    
    def __init__(self, course_id: int):
        super().__init__("Course", course_id)


class CourseNotAvailableException(DomainException):
    """Raised when a course is not available for enrollment"""
    
    def __init__(self, course_id: int, current_status: str):
        super().__init__(
            message=f"Course {course_id} is not available for enrollment. Current status: {current_status}",
            code="COURSE_NOT_AVAILABLE"
        )
        self.course_id = course_id
        self.current_status = current_status


class EnrollmentException(DomainException):
    """Base exception for enrollment errors"""
    pass


class AlreadyEnrolledException(EnrollmentException):
    """Raised when user is already enrolled in a course"""
    
    def __init__(self, user_id: int, course_id: int):
        super().__init__(
            message=f"User {user_id} is already enrolled in course {course_id}",
            code="ALREADY_ENROLLED"
        )
        self.user_id = user_id
        self.course_id = course_id


class NotEnrolledException(EnrollmentException):
    """Raised when user is not enrolled in a course"""
    
    def __init__(self, user_id: int, course_id: int):
        super().__init__(
            message=f"User {user_id} is not enrolled in course {course_id}",
            code="NOT_ENROLLED"
        )
        self.user_id = user_id
        self.course_id = course_id


class CannotUnenrollException(EnrollmentException):
    """Raised when unenrollment is not allowed"""
    
    def __init__(self, course_id: int, reason: str):
        super().__init__(
            message=f"Cannot unenroll from course {course_id}: {reason}",
            code="CANNOT_UNENROLL"
        )
        self.course_id = course_id
        self.reason = reason

