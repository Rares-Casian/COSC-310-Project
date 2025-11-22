"""User CRUD operations and password management."""
import uuid
from typing import Dict, Any, List, Optional
from passlib.context import CryptContext
from backend.authentication import utils as auth_utils
from backend.authentication.schemas import UserCreate, UserToken
from backend.users import schemas
from backend.core import exceptions


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def load_active_users() -> List[Dict[str, Any]]:
    return auth_utils.load_active_users()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    return auth_utils.get_user_by_id(user_id)


def add_user(new_user: UserCreate) -> Dict[str, Any]:
    users = load_active_users()
    if any(u.get("email") == new_user.email for u in users):
        raise exceptions.ConflictError("Email already registered.")

    user_obj = {
        "user_id": str(uuid.uuid4()),
        "username": new_user.username,
        "email": new_user.email,
        "hashed_password": pwd_context.hash(new_user.password),
        "role": new_user.role,
        "status": new_user.status,
        "movies_reviewed": [],
        "watch_later": [],
        "penalties": [],
    }
    users.append(user_obj)
    auth_utils.save_active_users(users)
    return user_obj


def update_user(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    users = load_active_users()
    for user in users:
        if user.get("user_id") == user_id:
            user.update(updates)
            auth_utils.save_active_users(users)
            return user
    raise exceptions.NotFoundError("User")


def change_password(user_id: str, old_password: str, new_password: str) -> None:
    users = load_active_users()
    for user in users:
        if user.get("user_id") == user_id:
            if not pwd_context.verify(old_password, user.get("hashed_password", "")):
                raise exceptions.AuthorizationError("Incorrect old password.")
            user["hashed_password"] = pwd_context.hash(new_password)
            auth_utils.save_active_users(users)
            return
    raise exceptions.NotFoundError("User")


def delete_user(user_id: str) -> None:
    users = load_active_users()
    updated = [u for u in users if u.get("user_id") != user_id]
    if len(updated) == len(users):
        raise exceptions.NotFoundError("User")
    auth_utils.save_active_users(updated)
