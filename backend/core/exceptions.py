"""Custom exception classes for consistent error handling across the application."""
from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class BaseAPIException(HTTPException):
    """Base exception class"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__


class ValidationError(BaseAPIException):
    """Raised when request validation fails."""
    def __init__(self, detail: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


class AuthenticationError(BaseAPIException):
    """Raised when authentication fails."""
    def __init__(self, detail: str = "Authentication required", error_code: str = "AUTHENTICATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code=error_code
        )


class AuthorizationError(BaseAPIException):
    """Raised when user lacks required permissions."""
    def __init__(self, detail: str = "Access denied", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )


class NotFoundError(BaseAPIException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str = "Resource", error_code: str = "NOT_FOUND"):
        detail = f"{resource} not found."
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code
        )


class ConflictError(BaseAPIException):
    """Raised when a resource conflict occurs (e.g., duplicate entry)."""
    def __init__(self, detail: str, error_code: str = "CONFLICT_ERROR"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code
        )


class BusinessLogicError(BaseAPIException):
    """Raised when business logic validation fails."""
    def __init__(self, detail: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


def raise_validation_error(message: str) -> None:
    """Raise a validation error with the given message."""
    raise ValidationError(detail=message)


def raise_not_found(resource: str) -> None:
    """Raise a not found error for the given resource."""
    raise NotFoundError(resource=resource)


def raise_authentication_error(message: str = "Authentication required") -> None:
    """Raise an authentication error with the given message."""
    raise AuthenticationError(detail=message)


def raise_authorization_error(message: str = "Access denied") -> None:
    """Raise an authorization error with the given message."""
    raise AuthorizationError(detail=message)

