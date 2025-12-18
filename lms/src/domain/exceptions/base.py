"""
Base Domain Exceptions
"""


class DomainException(Exception):
    """Base exception for all domain errors"""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'message': self.message,
        }


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found"""
    
    def __init__(self, entity_name: str, entity_id: any):
        super().__init__(
            message=f"{entity_name} with id {entity_id} not found",
            code="ENTITY_NOT_FOUND"
        )
        self.entity_name = entity_name
        self.entity_id = entity_id


class ValidationException(DomainException):
    """Raised when validation fails"""
    
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(
            message="; ".join(errors),
            code="VALIDATION_ERROR"
        )
    
    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'message': self.message,
            'errors': self.errors,
        }


class BusinessRuleViolationException(DomainException):
    """Raised when a business rule is violated"""
    
    def __init__(self, rule: str, message: str):
        self.rule = rule
        super().__init__(
            message=message,
            code="BUSINESS_RULE_VIOLATION"
        )
    
    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'rule': self.rule,
            'message': self.message,
        }

