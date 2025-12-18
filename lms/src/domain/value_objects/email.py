"""
Email Value Object
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """
    Email Value Object
    
    Immutable object representing a valid email address.
    """
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email format: {self.value}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def domain(self) -> str:
        """Get email domain"""
        return self.value.split('@')[1]
    
    @property
    def local_part(self) -> str:
        """Get local part of email (before @)"""
        return self.value.split('@')[0]

