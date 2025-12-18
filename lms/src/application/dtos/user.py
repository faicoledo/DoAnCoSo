"""
User DTOs
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class RegisterUserDTO:
    """DTO for user registration"""
    email: str
    full_name: str
    password: str
    password_confirm: str


@dataclass
class LoginDTO:
    """DTO for user login"""
    email: str
    password: str


@dataclass
class UpdateUserDTO:
    """DTO for updating user profile"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[any] = None  # File object
    password: Optional[str] = None
    password_confirm: Optional[str] = None


@dataclass
class EnrollmentResponseDTO:
    """DTO for enrollment in response"""
    course_id: int
    course_title: str
    subject_title: str
    role_in_course: str
    role_display: str
    status: str
    joined_at: datetime


@dataclass
class UserResponseDTO:
    """DTO for user response"""
    id: int
    email: str
    full_name: str
    role: str
    role_display: str
    avatar: Optional[str] = None
    phone: str = ""
    bio: str = ""
    enrollments: List[EnrollmentResponseDTO] = field(default_factory=list)
    
    @classmethod
    def from_entity(cls, user_entity, enrollments: List[EnrollmentResponseDTO] = None) -> 'UserResponseDTO':
        """Create DTO from UserEntity"""
        return cls(
            id=user_entity.id,
            email=user_entity.email,
            full_name=user_entity.full_name,
            role=user_entity.role.value if user_entity.role else "STUDENT",
            role_display=user_entity.role.display_name if user_entity.role else "Học viên",
            avatar=user_entity.profile.avatar if user_entity.profile else None,
            phone=user_entity.profile.phone if user_entity.profile else "",
            bio=user_entity.profile.bio if user_entity.profile else "",
            enrollments=enrollments or []
        )


@dataclass
class TokenResponseDTO:
    """DTO for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600  # seconds


@dataclass
class LoginResponseDTO:
    """DTO for login response"""
    user: UserResponseDTO
    tokens: TokenResponseDTO

