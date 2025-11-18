"""Security utilities for authentication and token management.

Includes:
- Password hashing and verification
- JWT creation and validation
- Password reset flow
- FastAPI dependency for current user
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from backend.authentication import schemas
from backend.core import tokens
from backend.authentication.security_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# -----------------------------------------------------------------------------
# PASSWORD HASHING
# -----------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plaintext password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# -----------------------------------------------------------------------------
# JWT CREATION AND VALIDATION
# -----------------------------------------------------------------------------
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token signature and return payload if valid and not revoked."""
    if tokens.is_token_revoked(token):
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None


# -----------------------------------------------------------------------------
# PASSWORD RESET TOKENS
# -----------------------------------------------------------------------------
def create_reset_token(user_id: str) -> str:
    """Generate a short-lived token for password reset."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    payload = {"sub": user_id, "scope": "password_reset", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> Optional[str]:
    """Validate a password-reset token and return user_id if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("scope") != "password_reset":
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


# -----------------------------------------------------------------------------
# FASTAPI DEPENDENCY: CURRENT USER
# -----------------------------------------------------------------------------
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> schemas.TokenData:
    """
    Extract the current user from the Authorization header and validate their status.
    Raises HTTP 401 if invalid or 403 if deactivated.
    """
    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("status") != schemas.UserStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    return schemas.TokenData(
        user_id=payload["sub"],
        role=payload["role"],
        status=payload["status"],
    )
