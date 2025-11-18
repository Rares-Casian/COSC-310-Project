"""User profile and admin CRUD schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserPublic(UserBase):
    user_id: str
    role: str
    status: str
    movies_reviewed: list[str] = []
    watch_later: list[str] = []
    penalties: list[str] = []


class UserSelfUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserAdminUpdate(UserSelfUpdate):
    role: Optional[str] = None
    status: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class StatusUpdate(BaseModel):
    status: str  # validated in router to be 'active' or 'inactive'
