from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRole(str, Enum):
    guest = "guest"
    member = "member"
    critic = "critic"
    moderator = "moderator"
    administrator = "administrator"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# --- Token payloads ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str
    role: str
    status: str

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.member
    status: UserStatus = UserStatus.ACTIVE


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    role: str
    status: str

    class Config:
        use_enum_values = True


class UserToken(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    role: str
    status: str

    class Config:
        use_enum_values = True
