"""User profile and administrative management routes."""
from fastapi import APIRouter, Depends, HTTPException
from backend.authentication.security import get_current_user
from backend.authentication.schemas import UserToken
from backend.users import utils, schemas
from backend.core.authz import require_role

router = APIRouter(prefix="/users", tags=["Users"])


# --- Self routes ---
@router.get("/me", response_model=schemas.UserPublic)
def get_my_profile(current_user: UserToken = Depends(get_current_user)):
    user = utils.get_user_by_id(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/me", response_model=schemas.UserPublic)
def update_my_profile(update: schemas.UserSelfUpdate, current_user: UserToken = Depends(get_current_user)):
    return utils.update_user(current_user.user_id, update.dict(exclude_unset=True))


@router.patch("/me/password")
def change_my_password(update: schemas.PasswordChange, current_user: UserToken = Depends(get_current_user)):
    utils.change_password(current_user.user_id, update.old_password, update.new_password)
    return {"message": "Password updated successfully."}


@router.patch("/me/status")
def change_my_status(update: schemas.StatusUpdate, current_user: UserToken = Depends(get_current_user)):
    if update.status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="Invalid status value.")
    return utils.update_user_status(current_user.user_id, update.status)


# --- Admin routes ---
@router.get("/", response_model=list[schemas.UserPublic])
def list_users(current_user: UserToken = Depends(get_current_user)):
    require_role(current_user, ["administrator"])
    return utils.load_active_users()


@router.get("/{user_id}", response_model=schemas.UserPublic)
def get_user(user_id: str, current_user: UserToken = Depends(get_current_user)):
    require_role(current_user, ["administrator"])
    user = utils.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/{user_id}", response_model=schemas.UserPublic)
def update_user_admin(user_id: str, update: schemas.UserAdminUpdate, current_user: UserToken = Depends(get_current_user)):
    require_role(current_user, ["administrator"])
    return utils.update_user(user_id, update.dict(exclude_unset=True))


@router.delete("/{user_id}")
def delete_user(user_id: str, current_user: UserToken = Depends(get_current_user)):
    require_role(current_user, ["administrator"])
    utils.delete_user(user_id)
    return {"message": f"User {user_id} deleted."}
