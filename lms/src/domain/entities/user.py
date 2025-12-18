"""
User Domain Entities
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum

from .base import Entity, AggregateRoot


class GlobalRole(str, Enum):
    """User roles in the system"""
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    
    @property
    def display_name(self) -> str:
        names = {
            "ADMIN": "Admin",
            "TEACHER": "Giáo viên",
            "STUDENT": "Học viên"
        }
        return names.get(self.value, self.value)


@dataclass
class UserProfile(Entity):
    """User Profile Entity"""
    user_id: int = None
    full_name: str = ""
    role: GlobalRole = GlobalRole.STUDENT
    avatar: Optional[str] = None
    phone: str = ""
    bio: str = ""
    
    def is_admin(self) -> bool:
        return self.role == GlobalRole.ADMIN
    
    def is_teacher(self) -> bool:
        return self.role == GlobalRole.TEACHER
    
    def is_student(self) -> bool:
        return self.role == GlobalRole.STUDENT
    
    def can_create_course(self) -> bool:
        """Check if user can create courses"""
        return self.role in [GlobalRole.ADMIN, GlobalRole.TEACHER]
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.role == GlobalRole.ADMIN


@dataclass
class UserEntity(AggregateRoot):
    """
    User Aggregate Root
    
    This is the main entry point for user-related operations.
    Combines Django User with UserProfile.
    """
    username: str = ""
    email: str = ""
    password_hash: str = field(default="", repr=False)
    is_active: bool = True
    last_login: Optional[datetime] = None
    profile: Optional[UserProfile] = None
    enrollments: List['EnrollmentEntity'] = field(default_factory=list)
    
    def __post_init__(self):
        if self.profile is None:
            self.profile = UserProfile()
    
    @property
    def full_name(self) -> str:
        """Get full name from profile"""
        if self.profile and self.profile.full_name:
            return self.profile.full_name
        return self.username
    
    @property
    def role(self) -> GlobalRole:
        """Get role from profile"""
        if self.profile:
            return self.profile.role
        return GlobalRole.STUDENT
    
    def update_profile(
        self, 
        email: str = None,
        full_name: str = None, 
        phone: str = None, 
        bio: str = None,
        avatar = None,
        password: str = None,
    ) -> None:
        """Update user profile information"""
        if self.profile is None:
            self.profile = UserProfile(user_id=self.id)
        
        if email is not None:
            self.email = email
            self.username = email  # Keep username in sync with email
        if full_name is not None:
            self.profile.full_name = full_name
        if phone is not None:
            self.profile.phone = phone
        if bio is not None:
            self.profile.bio = bio
        if avatar is not None:
            self.profile.avatar = avatar
        if password is not None:
            self.password_hash = password  # Will be hashed by repository
    
    def enroll_in_course(self, course_id: int, role: str = "STUDENT") -> 'EnrollmentEntity':
        """Enroll user in a course"""
        from .enrollment import EnrollmentEntity, CourseRole
        
        # Check if already enrolled
        for enrollment in self.enrollments:
            if enrollment.course_id == course_id:
                raise ValueError("User is already enrolled in this course")
        
        enrollment = EnrollmentEntity(
            user_id=self.id,
            course_id=course_id,
            role_in_course=CourseRole(role)
        )
        self.enrollments.append(enrollment)
        return enrollment
    
    def unenroll_from_course(self, course_id: int) -> bool:
        """Remove user enrollment from a course"""
        for i, enrollment in enumerate(self.enrollments):
            if enrollment.course_id == course_id:
                self.enrollments.pop(i)
                return True
        return False
    
    def is_enrolled_in(self, course_id: int) -> bool:
        """Check if user is enrolled in a specific course"""
        return any(e.course_id == course_id for e in self.enrollments)
    
    def get_enrollment(self, course_id: int) -> Optional['EnrollmentEntity']:
        """Get enrollment for a specific course"""
        for enrollment in self.enrollments:
            if enrollment.course_id == course_id:
                return enrollment
        return None

