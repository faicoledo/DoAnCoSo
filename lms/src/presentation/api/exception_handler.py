"""
Custom Exception Handler for DRF

Converts domain exceptions to proper HTTP responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from ...domain.exceptions.base import (
    DomainException,
    EntityNotFoundException,
    ValidationException,
    BusinessRuleViolationException,
)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that handles domain exceptions.
    """
    # First, handle standard DRF exceptions
    response = exception_handler(exc, context)
    
    if response is not None:
        return response
    
    # Handle domain exceptions
    if isinstance(exc, EntityNotFoundException):
        return Response(
            {'detail': exc.message, 'code': exc.code},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if isinstance(exc, ValidationException):
        return Response(
            exc.to_dict(),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(exc, BusinessRuleViolationException):
        return Response(
            exc.to_dict(),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(exc, DomainException):
        return Response(
            {'detail': exc.message, 'code': exc.code},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # For unhandled exceptions, return generic error
    return Response(
        {'detail': 'Internal server error', 'code': 'INTERNAL_ERROR'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

