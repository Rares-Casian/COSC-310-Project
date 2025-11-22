"""Centralized validation functions for user input validation."""
import re
from typing import List, Tuple
from backend.core import exceptions


# constants
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20
PASSWORD_MIN_LENGTH = 8
SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:',.<>?/`~"


def validate_username(username: str) -> None:
    """
    Validate username format and length.
    Raises ValidationError if validation fails.
    """
    if not username:
        raise exceptions.ValidationError("Username is required.")
    
    if len(username) < USERNAME_MIN_LENGTH or len(username) > USERNAME_MAX_LENGTH:
        raise exceptions.ValidationError(
            f"Username must be between {USERNAME_MIN_LENGTH} and {USERNAME_MAX_LENGTH} characters long."
        )
    
    if not username.isalnum():
        raise exceptions.ValidationError(
            "Username can only contain letters and numbers (no spaces or symbols)."
        )


def validate_password(password: str) -> None:
    """
    Validate password strength requirements.
    Raises ValidationError if validation fails.
    """
    if not password:
        raise exceptions.ValidationError("Password is required.")
    
    if len(password) < PASSWORD_MIN_LENGTH:
        raise exceptions.ValidationError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
        )
    
    if not any(c.isupper() for c in password):
        raise exceptions.ValidationError("Password must include at least one uppercase letter.")
    
    if not any(c.islower() for c in password):
        raise exceptions.ValidationError("Password must include at least one lowercase letter.")
    
    if not any(c.isdigit() for c in password):
        raise exceptions.ValidationError("Password must include at least one number.")
    
    if not any(c in SPECIAL_CHARS for c in password):
        raise exceptions.ValidationError("Password must include at least one special character.")


def validate_email(email: str) -> None:
    """
    Validate email format.
    Raises ValidationError if validation fails.
    """
    if not email:
        raise exceptions.ValidationError("Email is required.")
    
    # email validation
    if "@" not in email:
        raise exceptions.ValidationError("Invalid email address format.")
    
    parts = email.split("@")
    if len(parts) != 2:
        raise exceptions.ValidationError("Invalid email address format.")
    
    local, domain = parts
    if not local or not domain:
        raise exceptions.ValidationError("Invalid email address format.")
    
    if "." not in domain:
        raise exceptions.ValidationError("Invalid email address format.")
    
    # email regex validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise exceptions.ValidationError("Invalid email address format.")


def validate_user_registration(username: str, email: str, password: str) -> None:
    """
    Validate all user registration fields.
    Raises ValidationError if any validation fails.
    """
    validate_username(username)
    validate_email(email)
    validate_password(password)

