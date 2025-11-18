from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Item not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationError(HTTPException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

  def movie_not_found(movie_id: str = None) -> NotFoundError:
    detail = f"Movie not found" + (f" (ID: {movie_id})" if movie_id else "")
    return NotFoundError(detail=detail)


def review_not_found(review_id: str = None) -> NotFoundError:
    detail = f"Review not found" + (f" (ID: {review_id})" if review_id else "")
    return NotFoundError(detail=detail)


def user_not_found(user_id: str = None) -> NotFoundError:
    detail = f"User not found" + (f" (ID: {user_id})" if user_id else "")
    return NotFoundError(detail=detail)


def not_authorized(detail: str = "Not authorized to perform this action") -> ForbiddenError:
    return ForbiddenError(detail=detail)
