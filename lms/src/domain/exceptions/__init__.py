"""
Domain Exceptions
"""
from .base import DomainException
from .user import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
)
from .course import (
    CourseNotFoundException,
    CourseNotAvailableException,
    EnrollmentException,
)
from .assessment import (
    AssignmentNotFoundException,
    AttemptLimitExceededException,
    AssignmentNotAvailableException,
)

__all__ = [
    'DomainException',
    'UserNotFoundException',
    'UserAlreadyExistsException',
    'InvalidCredentialsException',
    'CourseNotFoundException',
    'CourseNotAvailableException',
    'EnrollmentException',
    'AssignmentNotFoundException',
    'AttemptLimitExceededException',
    'AssignmentNotAvailableException',
]

