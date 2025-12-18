"""
Assessment Domain Exceptions
"""
from .base import DomainException, EntityNotFoundException


class AssignmentNotFoundException(EntityNotFoundException):
    """Raised when an assignment is not found"""
    
    def __init__(self, assignment_id: int):
        super().__init__("Assignment", assignment_id)


class AssignmentNotAvailableException(DomainException):
    """Raised when assignment is not available"""
    
    def __init__(self, assignment_id: int, reason: str):
        super().__init__(
            message=f"Assignment {assignment_id} is not available: {reason}",
            code="ASSIGNMENT_NOT_AVAILABLE"
        )
        self.assignment_id = assignment_id
        self.reason = reason


class AttemptLimitExceededException(DomainException):
    """Raised when user has exceeded allowed attempts"""
    
    def __init__(self, assignment_id: int, max_attempts: int):
        super().__init__(
            message=f"Maximum attempts ({max_attempts}) exceeded for assignment {assignment_id}",
            code="ATTEMPT_LIMIT_EXCEEDED"
        )
        self.assignment_id = assignment_id
        self.max_attempts = max_attempts


class AttemptAlreadySubmittedException(DomainException):
    """Raised when trying to modify a submitted attempt"""
    
    def __init__(self, attempt_id: int):
        super().__init__(
            message=f"Attempt {attempt_id} has already been submitted",
            code="ATTEMPT_ALREADY_SUBMITTED"
        )
        self.attempt_id = attempt_id


class QuestionNotFoundException(EntityNotFoundException):
    """Raised when a question is not found"""
    
    def __init__(self, question_id: int):
        super().__init__("Question", question_id)

