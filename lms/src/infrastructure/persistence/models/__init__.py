"""
Django ORM Models

These models map directly to database tables.
They are implementation details of the Infrastructure layer.

Các bảng chính:
- User & Profile: Người dùng
- Course structure: Subject → Course → Module → Lesson
- Content: Resource (tài liệu)
- Assessment: Assignment → Question, Attempt → AttemptDetail
- Activity & Communication: Logs, Notifications, Comments
"""
from .user import UserProfileModel
from .course import SubjectModel, CourseModel, ModuleModel, LessonModel
from .enrollment import EnrollmentModel
from .content import ResourceModel
from .assessment import AssignmentModel, QuestionModel, AttemptModel, AttemptDetailModel
from .activity import UserActivityLogModel
from .communication import NotificationModel, CommentModel

__all__ = [
    # User
    'UserProfileModel',
    
    # Course structure
    'SubjectModel',
    'CourseModel', 
    'ModuleModel',
    'LessonModel',
    
    # Enrollment
    'EnrollmentModel',
    
    # Content
    'ResourceModel',
    
    # Assessment
    'AssignmentModel',
    'QuestionModel',
    'AttemptModel',
    'AttemptDetailModel',
    
    # Activity & Communication
    'UserActivityLogModel',
    'NotificationModel',
    'CommentModel',
]
