from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from backend.authentication import schemas, utils, security
from backend.core import tokens, exceptions, validators
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer()


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate):
    """Register a new user with validated input."""
    # Validate registration fields
    validators.validate_user_registration(user.username, user.email, user.password)
    
    exists, message = utils.user_exists(user.username, user.email)
    if exists:
        raise exceptions.ConflictError(message)

    new_user = {
        "user_id": str(uuid.uuid4()),
        "username": user.username,
        "email": user.email,
        "hashed_password": security.hash_password(user.password),
        "role": user.role.value,
        "status": schemas.UserStatus.ACTIVE.value,
        "movies_reviewed": [],
        "watch_later": [],
        "penalties": [],
    }

    utils.add_user(new_user, active=True)

    return {k: new_user[k] for k in ("user_id", "username", "email", "role", "status")}



@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = utils.get_user_by_username_or_email(form_data.username)
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise exceptions.AuthenticationError("Invalid username/email or password")

    if user["status"] != schemas.UserStatus.ACTIVE.value:
        raise exceptions.AuthorizationError("Account is deactivated")

    access_token = security.create_access_token(
        data={"sub": user["user_id"], "role": user["role"], "status": user["status"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    tokens.revoke_token(credentials.credentials)
    return {"message": "Logged out successfully."}


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(current_user: schemas.TokenData = Depends(security.get_current_user)):
    token = security.create_access_token(
        data={"sub": current_user.user_id, "role": current_user.role, "status": current_user.status}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/password/request")
def request_password_reset(email: str):
    users = utils.load_all_users()
    user = next((u for u in users if u["email"] == email), None)
    if not user:
        raise exceptions.NotFoundError("Email")

    token = security.create_reset_token(user["user_id"])
    return {"reset_token": token, "message": "Use this token within 10 minutes."}


@router.post("/password/reset")
def reset_password(token: str, new_password: str):
    """Reset user password with validated new password."""
    user_id = security.verify_reset_token(token)
    if not user_id:
        raise exceptions.ValidationError("Invalid or expired token")
    
    # Validate new password requirements
    validators.validate_password(new_password)

    users = utils.load_all_users()
    for user in users:
        if user["user_id"] == user_id:
            user["hashed_password"] = security.hash_password(new_password)
            break
    else:
        raise exceptions.NotFoundError("User")

    active = [u for u in users if u["status"] == "active"]
    inactive = [u for u in users if u["status"] == "inactive"]
    utils.save_active_users(active)
    utils.save_inactive_users(inactive)
    return {"message": "Password successfully reset"}


@router.get("/me")
def read_current_user(current_user: schemas.UserToken = Depends(security.get_current_user)):
    return current_user
