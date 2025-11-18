"""Authentication utilities: load/save users, handle revoked tokens."""
from typing import Any, Dict, List, Optional, Tuple
from backend.core.paths import (
    USERS_ACTIVE_FILE, USERS_INACTIVE_FILE, REVOKED_TOKENS_FILE
)
from backend.core.jsonio import load_json, save_json
from backend.authentication import schemas


# ----- User lists -----

def load_active_users() -> List[Dict[str, Any]]:
    return load_json(USERS_ACTIVE_FILE, default=[])


def save_active_users(users: List[Dict[str, Any]]) -> None:
    save_json(USERS_ACTIVE_FILE, users)


def load_inactive_users() -> List[Dict[str, Any]]:
    return load_json(USERS_INACTIVE_FILE, default=[])


def save_inactive_users(users: List[Dict[str, Any]]) -> None:
    save_json(USERS_INACTIVE_FILE, users)


def load_all_users() -> List[Dict[str, Any]]:
    return load_active_users() + load_inactive_users()


# ----- Helpers -----

def user_exists(username: str, email: str) -> Tuple[bool, Optional[str]]:
    users = load_all_users()
    username_taken = any(u.get("username") == username for u in users)
    email_taken = any(u.get("email") == email for u in users)
    if username_taken and email_taken:
        return True, "Username and Email already taken"
    if username_taken:
        return True, "Username already taken"
    if email_taken:
        return True, "Email already taken"
    return False, None


def add_user(user: Dict[str, Any], *, active: bool = True) -> None:
    """Add user to the active or inactive list."""
    user.setdefault("penalties", [])
    if active:
        users = load_active_users()
        users.append(user)
        save_active_users(users)
    else:
        users = load_inactive_users()
        users.append(user)
        save_inactive_users(users)


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    return next((u for u in load_all_users() if u.get("user_id") == user_id), None)

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    return next((u for u in load_all_users() if u.get("username") == username), None)

def get_user_by_username_or_email(identifier: str) -> Optional[Dict[str, Any]]:
    """Return a user by either username or email (case-insensitive for email)."""
    users = load_all_users()
    for u in users:
        if u.get("username") == identifier or u.get("email").lower() == identifier.lower():
            return u
    return None

def update_user_status(user_id: str, status: schemas.UserStatus) -> bool:
    """Move user between active/inactive and update status."""
    active_users = load_active_users()
    inactive_users = load_inactive_users()
    user = None

    active_users = [u for u in active_users if not (u.get("user_id") == user_id and (user := u))]
    inactive_users = [u for u in inactive_users if not (u.get("user_id") == user_id and (user := u))]
    if not user:
        return False

    user["status"] = status.value
    if status == schemas.UserStatus.ACTIVE:
        active_users.append(user)
    else:
        inactive_users.append(user)

    save_active_users(active_users)
    save_inactive_users(inactive_users)
    return True


# ----- Revoked tokens -----

def load_revoked_tokens() -> List[str]:
    return load_json(REVOKED_TOKENS_FILE, default=[])


def save_revoked_tokens(tokens: List[str]) -> None:
    save_json(REVOKED_TOKENS_FILE, tokens)
