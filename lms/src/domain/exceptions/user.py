"""
User Domain Exceptions
"""
from .base import DomainException, EntityNotFoundException


class UserNotFoundException(EntityNotFoundException):
    """Raised when a user is not found"""
    
    def __init__(self, user_id: any = None, email: str = None):
        if email:
            super(DomainException, self).__init__(f"User with email {email} not found")
            self.code = "USER_NOT_FOUND"
            self.message = f"User with email {email} not found"
        else:
            super().__init__("User", user_id)


class UserAlreadyExistsException(DomainException):
    """Raised when trying to create a user that already exists"""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"User with email {email} already exists",
            code="USER_ALREADY_EXISTS"
        )
        self.email = email


class InvalidCredentialsException(DomainException):
    """Raised when login credentials are invalid"""
    
    def __init__(self):
        super().__init__(
            message="Email hoặc mật khẩu không đúng",
            code="INVALID_CREDENTIALS"
        )


class InsufficientPermissionsException(DomainException):
    """Raised when user doesn't have required permissions"""
    
    def __init__(self, required_permission: str):
        super().__init__(
            message=f"Insufficient permissions. Required: {required_permission}",
            code="INSUFFICIENT_PERMISSIONS"
        )
        self.required_permission = required_permission

