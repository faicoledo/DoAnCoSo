"""
Password Value Object
"""
import hashlib
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class Password:
    """
    Password Value Object
    
    Handles password validation and hashing.
    """
    hashed_value: str
    
    MIN_LENGTH = 8
    
    @classmethod
    def create(cls, plain_password: str) -> 'Password':
        """Create a password from plain text"""
        cls._validate(plain_password)
        hashed = cls._hash(plain_password)
        return cls(hashed_value=hashed)
    
    @classmethod
    def from_hash(cls, hashed_value: str) -> 'Password':
        """Create a password from existing hash"""
        return cls(hashed_value=hashed_value)
    
    @staticmethod
    def _validate(password: str) -> None:
        """Validate password requirements"""
        errors = []
        
        if len(password) < Password.MIN_LENGTH:
            errors.append(f"Password must be at least {Password.MIN_LENGTH} characters")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if errors:
            raise ValueError("; ".join(errors))
    
    @staticmethod
    def _hash(password: str) -> str:
        """Hash password using SHA256 (Note: Use Django's make_password in production)"""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${hashed}"
    
    def verify(self, plain_password: str) -> bool:
        """Verify plain password against hash"""
        if '$' not in self.hashed_value:
            return False
        salt, stored_hash = self.hashed_value.split('$', 1)
        computed_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return computed_hash == stored_hash
    
    def __str__(self) -> str:
        return "********"

