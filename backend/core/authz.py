"""Authorization helpers for role and penalty checks."""
from functools import wraps
from fastapi import Depends
from backend.authentication.security import get_current_user
from backend.penalties import utils as penalty_utils
from backend.users import utils as user_utils
from backend.penalties import schemas
from backend.core import exceptions



def require_role(user, allowed_roles: list[str]):
    """Raise 403 if user does not have one of the allowed roles."""
    if user.role not in allowed_roles:
        raise exceptions.AuthorizationError(f"Access denied: requires one of {allowed_roles}.")



def block_if_penalized(blocked_types: list[str]):
    """
    Decorator that blocks actions if the current user has an active penalty
    matching one of the specified blocked types.
    Guest users are not subject to penalty checks.

    Example:
        @router.post("/reviews")
        @block_if_penalized(["review_ban", "suspension"])
        async def create_review(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            # Skip penalty checks for guest users
            if current_user.user_id == "guest" or current_user.role == "guest":
                return await func(*args, current_user=current_user, **kwargs)
            
            # Get user's active penalties (resolves expiries)
            penalties = penalty_utils.get_penalties_for_user(current_user.user_id)
            active_penalties = [
                p for p in penalties
                if p.status == schemas.PenaltyStatus.active and not p.has_expired()
            ]

            # Check if any match blocked types
            for p in active_penalties:
                if p.type.value in blocked_types:
                    raise exceptions.AuthorizationError(f"Action blocked due to active {p.type.value} penalty.")

            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
