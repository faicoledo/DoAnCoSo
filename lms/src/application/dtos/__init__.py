"""
Data Transfer Objects (DTOs)

DTOs are simple objects used to transfer data between layers.
They help decouple the domain layer from the presentation layer.
"""
from .user import (
    RegisterUserDTO,
    LoginDTO,
    UserResponseDTO,
    UpdateUserDTO,
)
from .course import (
    CourseDTO,
    CourseListDTO,
    EnrollmentDTO,
    ModuleDTO,
    LessonDTO,
)
from .assessment import (
    AssignmentDTO,
    QuestionDTO,
    AttemptDTO,
    SubmitAnswerDTO,
)

__all__ = [
    'RegisterUserDTO',
    'LoginDTO',
    'UserResponseDTO',
    'UpdateUserDTO',
    'CourseDTO',
    'CourseListDTO',
    'EnrollmentDTO',
    'ModuleDTO',
    'LessonDTO',
    'AssignmentDTO',
    'QuestionDTO',
    'AttemptDTO',
    'SubmitAnswerDTO',
]

