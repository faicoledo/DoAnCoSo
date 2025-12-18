"""
Domain Interfaces (Ports)

These are abstract interfaces that define contracts for repositories.
The Infrastructure layer will provide concrete implementations.
"""
from .repositories import (
    IUserRepository,
    ICourseRepository,
    IEnrollmentRepository,
    IAssignmentRepository,
    IProgressRepository,
)

__all__ = [
    'IUserRepository',
    'ICourseRepository',
    'IEnrollmentRepository',
    'IAssignmentRepository',
    'IProgressRepository',
]

