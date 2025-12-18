"""
Authentication Use Cases
"""
from dataclasses import dataclass
from typing import Optional

from .base import UseCase
from ..dtos.user import (
    RegisterUserDTO,
    LoginDTO,
    UpdateUserDTO,
    UserResponseDTO,
    LoginResponseDTO,
    TokenResponseDTO,
)
from ...domain.interfaces import IUserRepository, IEnrollmentRepository
from ...domain.entities.user import UserEntity, UserProfile, GlobalRole
from ...domain.exceptions.user import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
)


class RegisterUserUseCase(UseCase[RegisterUserDTO, UserResponseDTO]):
    """
    Use case for registering a new user.
    
    Steps:
    1. Validate input data
    2. Check if email already exists
    3. Create user entity
    4. Persist user
    5. Return user response
    """
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def execute(self, input_dto: RegisterUserDTO) -> UserResponseDTO:
        # Validate passwords match
        if input_dto.password != input_dto.password_confirm:
            raise ValueError("Mật khẩu xác nhận không khớp")
        
        # Check if email exists
        if self.user_repository.exists_by_email(input_dto.email):
            raise UserAlreadyExistsException(input_dto.email)
        
        # Create user entity
        user = UserEntity(
            username=input_dto.email,
            email=input_dto.email,
            profile=UserProfile(
                full_name=input_dto.full_name,
                role=GlobalRole.STUDENT,
            )
        )
        
        # Save user (repository handles password hashing)
        self.user_repository.save(user)
        
        return UserResponseDTO.from_entity(user)


class LoginUseCase(UseCase[LoginDTO, LoginResponseDTO]):
    """
    Use case for user login.
    
    Steps:
    1. Find user by email
    2. Verify password
    3. Generate tokens
    4. Return login response
    """
    
    def __init__(
        self, 
        user_repository: IUserRepository,
        token_service  # Token generation service
    ):
        self.user_repository = user_repository
        self.token_service = token_service
    
    def execute(self, input_dto: LoginDTO) -> LoginResponseDTO:
        # Find user by email
        user = self.user_repository.find_by_email(input_dto.email)
        if not user:
            raise InvalidCredentialsException()
        
        # Verify password (delegated to repository/auth service)
        if not self.token_service.verify_password(input_dto.password, user.password_hash):
            raise InvalidCredentialsException()
        
        # Generate tokens
        access_token, refresh_token = self.token_service.generate_tokens(user)
        
        return LoginResponseDTO(
            user=UserResponseDTO.from_entity(user),
            tokens=TokenResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token,
            )
        )


@dataclass
class GetCurrentUserInput:
    """Input for GetCurrentUserUseCase"""
    user_id: int


class GetCurrentUserUseCase(UseCase[GetCurrentUserInput, UserResponseDTO]):
    """
    Use case for getting current user profile.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        enrollment_repository: IEnrollmentRepository,
    ):
        self.user_repository = user_repository
        self.enrollment_repository = enrollment_repository
    
    def execute(self, input_dto: GetCurrentUserInput) -> UserResponseDTO:
        user = self.user_repository.find_by_id(input_dto.user_id)
        if not user:
            raise UserNotFoundException(user_id=input_dto.user_id)
        
        # Get enrollments
        enrollments = self.enrollment_repository.find_by_user(input_dto.user_id)
        
        # Build enrollment DTOs
        from ..dtos.user import EnrollmentResponseDTO
        enrollment_dtos = []
        for e in enrollments:
            enrollment_dtos.append(EnrollmentResponseDTO(
                course_id=e.course_id,
                course_title="",  # Would need to fetch from course repo
                subject_title="",
                role_in_course=e.role_in_course.value,
                role_display=e.role_in_course.display_name,
                status="",
                joined_at=e.joined_at,
            ))
        
        return UserResponseDTO.from_entity(user, enrollment_dtos)


@dataclass
class UpdateUserInput:
    """Input for UpdateUserProfileUseCase"""
    user_id: int
    data: UpdateUserDTO


class UpdateUserProfileUseCase(UseCase[UpdateUserInput, UserResponseDTO]):
    """
    Use case for updating user profile.
    """
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def execute(self, input_dto: UpdateUserInput) -> UserResponseDTO:
        user = self.user_repository.find_by_id(input_dto.user_id)
        if not user:
            raise UserNotFoundException(user_id=input_dto.user_id)
        
        data = input_dto.data
        
        # Validate email change if provided
        if data.email and data.email != user.email:
            if self.user_repository.exists_by_email(data.email):
                raise UserAlreadyExistsException(data.email)
        
        # Validate password change if provided
        if data.password:
            if data.password != data.password_confirm:
                raise ValueError("Mật khẩu xác nhận không khớp")
        
        # Update profile
        user.update_profile(
            email=data.email,
            full_name=data.full_name,
            phone=data.phone,
            bio=data.bio,
            avatar=data.avatar,
            password=data.password,
        )
        
        # Save changes
        self.user_repository.save(user)
        
        return UserResponseDTO.from_entity(user)

