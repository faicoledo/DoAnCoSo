"""
Use Cases - Application-specific business rules

Each use case represents a single action that can be performed by the user.
Use cases orchestrate the flow of data and domain entities.
"""
from .auth import (
    RegisterUserUseCase,
    LoginUseCase,
    GetCurrentUserUseCase,
    UpdateUserProfileUseCase,
)
from .enrollment import (
    EnrollInCourseUseCase,
    UnenrollFromCourseUseCase,
    GetMyCoursesUseCase,
    GetCourseStudentsUseCase,
)
from .course import (
    GetCourseDetailUseCase,
    ListCoursesUseCase,
)
from .notification import (
    CreateNotificationUseCase,
    MarkNotificationAsReadUseCase,
    ListUserNotificationsUseCase,
)
from .comment import (
    CreateCommentUseCase,
    ListCommentsUseCase,
)
from .activity_log import (
    LogActivityUseCase,
    ListActivityLogsUseCase,
)

__all__ = [
    'RegisterUserUseCase',
    'LoginUseCase',
    'GetCurrentUserUseCase',
    'UpdateUserProfileUseCase',
    'EnrollInCourseUseCase',
    'UnenrollFromCourseUseCase',
    'GetMyCoursesUseCase',
    'GetCourseStudentsUseCase',
    'GetCourseDetailUseCase',
    'ListCoursesUseCase',
    'CreateNotificationUseCase',
    'MarkNotificationAsReadUseCase',
    'ListUserNotificationsUseCase',
    'CreateCommentUseCase',
    'ListCommentsUseCase',
    'LogActivityUseCase',
    'ListActivityLogsUseCase',
]

