"""Custom exception classes for consistent error handling across the application."""
from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """Raise when a resource is not found (404)."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedError(HTTPException):
    """Raise when authentication is required or invalid (401)."""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(HTTPException):
    """Raise when access is forbidden (403)."""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationError(HTTPException):
    """Raise when validation fails (400)."""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


# Convenience functions for common error messages
def movie_not_found(movie_id: str = None) -> NotFoundError:
    """Return a NotFoundError for a movie."""
    detail = f"Movie not found" + (f" (ID: {movie_id})" if movie_id else "")
    return NotFoundError(detail=detail)


def review_not_found(review_id: str = None) -> NotFoundError:
    """Return a NotFoundError for a review."""
    detail = f"Review not found" + (f" (ID: {review_id})" if review_id else "")
    return NotFoundError(detail=detail)


def user_not_found(user_id: str = None) -> NotFoundError:
    """Return a NotFoundError for a user."""
    detail = f"User not found" + (f" (ID: {user_id})" if user_id else "")
    return NotFoundError(detail=detail)


def not_authorized(detail: str = "Not authorized to perform this action") -> ForbiddenError:
    """Return a ForbiddenError for authorization failures."""
    return ForbiddenError(detail=detail)
