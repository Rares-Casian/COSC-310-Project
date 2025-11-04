"""Authentication endpoints: register, login, logout, refresh, password reset."""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from backend.authentication import schemas, utils, security
from backend.core import tokens
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer()


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate):
    """Register a new user (with username and password validation)."""

    # --- Username Validation ---
    if len(user.username) < 3 or len(user.username) > 20:
        raise HTTPException(status_code=400, detail="Username must be between 3 and 20 characters long.")
    if not user.username.isalnum():
        raise HTTPException(status_code=400, detail="Username can only contain letters and numbers (no spaces or symbols).")

    # --- Password Validation ---
    password = user.password
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="Password must include at least one uppercase letter.")
    if not any(c.islower() for c in password):
        raise HTTPException(status_code=400, detail="Password must include at least one lowercase letter.")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="Password must include at least one number.")
    if not any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/`~" for c in password):
        raise HTTPException(status_code=400, detail="Password must include at least one special character.")

    # --- Email Validation ---
    if "@" not in user.email or "." not in user.email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid email address format.")

    # --- Existing user check ---
    exists, message = utils.user_exists(user.username, user.email)
    if exists:
        raise HTTPException(status_code=400, detail=message)

    # --- Create User ---
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
    """Authenticate user and issue an access token."""
    user = utils.get_user_by_username_or_email(form_data.username)
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")

    if user["status"] != schemas.UserStatus.ACTIVE.value:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    access_token = security.create_access_token(
        data={"sub": user["user_id"], "role": user["role"], "status": user["status"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Revoke the current access token."""
    tokens.revoke_token(credentials.credentials)
    return {"message": "Logged out successfully."}


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(current_user: schemas.TokenData = Depends(security.get_current_user)):
    """Issue a new access token for the authenticated user."""
    token = security.create_access_token(
        data={"sub": current_user.user_id, "role": current_user.role, "status": current_user.status}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/password/request")
def request_password_reset(email: str):
    """Simulated password reset request (returns token for development)."""
    users = utils.load_all_users()
    user = next((u for u in users if u["email"] == email), None)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    token = security.create_reset_token(user["user_id"])
    return {"reset_token": token, "message": "Use this token within 10 minutes."}


@router.post("/password/reset")
def reset_password(token: str, new_password: str):
    """Confirm password reset and persist hashed password to correct file."""
    user_id = security.verify_reset_token(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    users = utils.load_all_users()
    for user in users:
        if user["user_id"] == user_id:
            user["hashed_password"] = security.hash_password(new_password)
            break
    else:
        raise HTTPException(status_code=404, detail="User not found")

    active = [u for u in users if u["status"] == "active"]
    inactive = [u for u in users if u["status"] == "inactive"]
    utils.save_active_users(active)
    utils.save_inactive_users(inactive)
    return {"message": "Password successfully reset"}


@router.get("/me")
def read_current_user(current_user: schemas.UserToken = Depends(security.get_current_user)):
    return current_user