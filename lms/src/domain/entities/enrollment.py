"""
Enrollment Domain Entity
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

from .base import Entity


class CourseRole(str, Enum):
    """Role of user within a course"""
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    TA = "TA"  # Teaching Assistant
    
    @property
    def display_name(self) -> str:
        names = {
            "TEACHER": "Giáo viên",
            "STUDENT": "Học viên",
            "TA": "Trợ giảng"
        }
        return names.get(self.value, self.value)


@dataclass
class EnrollmentEntity(Entity):
    """
    Enrollment Entity
    
    Represents the relationship between a User and a Course.
    This is the basis for access control to course content.
    """
    user_id: int = None
    course_id: int = None
    role_in_course: CourseRole = CourseRole.STUDENT
    joined_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"User {self.user_id} - Course {self.course_id} ({self.role_in_course.display_name})"
    
    # ==================== Role Checks ====================
    
    def is_teacher(self) -> bool:
        """Check if enrollment is for a teacher"""
        return self.role_in_course == CourseRole.TEACHER
    
    def is_student(self) -> bool:
        """Check if enrollment is for a student"""
        return self.role_in_course == CourseRole.STUDENT
    
    def is_teaching_assistant(self) -> bool:
        """Check if enrollment is for a TA"""
        return self.role_in_course == CourseRole.TA
    
    def can_grade(self) -> bool:
        """Check if user can grade assignments"""
        return self.role_in_course in [CourseRole.TEACHER, CourseRole.TA]
    
    def can_manage_content(self) -> bool:
        """Check if user can manage course content"""
        return self.role_in_course == CourseRole.TEACHER
    
    def can_view_all_students(self) -> bool:
        """Check if user can view all students in the course"""
        return self.role_in_course in [CourseRole.TEACHER, CourseRole.TA]
    
    # ==================== Role Management ====================
    
    def promote_to_ta(self) -> None:
        """Promote student to TA"""
        if self.role_in_course != CourseRole.STUDENT:
            raise ValueError("Only students can be promoted to TA")
        self.role_in_course = CourseRole.TA
    
    def demote_to_student(self) -> None:
        """Demote TA to student"""
        if self.role_in_course != CourseRole.TA:
            raise ValueError("Only TAs can be demoted to student")
        self.role_in_course = CourseRole.STUDENT

