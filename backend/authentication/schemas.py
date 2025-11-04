from pydantic import BaseModel, EmailStr, validator
import re
from enum import Enum
from typing import List, Optional, Dict

# User Roles
class UserRole(str, Enum):
    GUEST = "guest"
    MEMBER = "member"
    CRITIC = "critic"
    MODERATOR = "moderator"
    ADMINISTRATOR = "administrator"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# User Registration
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.MEMBER 

    # Username Validation
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    # Password Validation
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if len(v) > 72:
            raise ValueError("Password cannot exceed 72 characters")
        return v

# User Response
class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    status: str
    movies_reviewed: List = []
    watch_later: List = []
    penalties: List[Dict] = []

# User Login
class UserLogin(BaseModel):
    username: str
    password: str

# Token Response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Token Data
class TokenData(BaseModel):
    user_id: Optional[str] = None  # 👤 User identifier
    role: Optional[str] = None     # 🎭 User role for authorization
    status: Optional[str] = None
