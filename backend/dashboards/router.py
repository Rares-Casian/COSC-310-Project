"""Role-specific dashboard endpoints."""
from fastapi import APIRouter, Depends
from typing import Dict, List

from backend.authentication.security import get_current_user
from backend.authentication.schemas import UserToken
from backend.users import utils as user_utils
from backend.core import exceptions

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


ROLE_ACTIONS: Dict[str, List[str]] = {
    "guest": [
        "Browse public reviews",
        "Preview trending movies",
    ],
    "member": [
        "Manage your watchlist",
        "Log and rate movies",
        "Write reviews",
    ],
    "critic": [
        "Publish critic-grade reviews",
        "Highlight featured picks",
        "Collaborate on reports",
    ],
    "moderator": [
        "Review reports and flags",
        "Manage penalties for users",
        "Oversee community content",
    ],
    "administrator": [
        "Manage users and roles",
        "Oversee reports and system settings",
        "Audit penalties and escalations",
    ],
}


def _dashboard_payload(current_user: UserToken, role: str) -> Dict:
    user = user_utils.get_user_by_id(current_user.user_id) or {}
    return {
        "user": {
            "user_id": user.get("user_id", current_user.user_id),
            "username": user.get("username", ""),
            "email": user.get("email", ""),
            "role": role,
            "status": current_user.status,
        },
        "actions": ROLE_ACTIONS.get(role, []),
        "links": [
            {"label": "Home", "href": "/"},
            {"label": "Watchlist", "href": "/watchlist"},
            {"label": "Reviews", "href": "/reviews"},
        ],
    }


def _enforce_role(current_user: UserToken, required_role: str):
    if current_user.role != required_role:
        raise exceptions.AuthorizationError(f"Access denied: requires role '{required_role}'.")


@router.get("/guest")
def guest_dashboard(current_user: UserToken = Depends(get_current_user)):
    _enforce_role(current_user, "guest")
    return _dashboard_payload(current_user, "guest")


@router.get("/member")
def member_dashboard(current_user: UserToken = Depends(get_current_user)):
    _enforce_role(current_user, "member")
    return _dashboard_payload(current_user, "member")


@router.get("/critic")
def critic_dashboard(current_user: UserToken = Depends(get_current_user)):
    _enforce_role(current_user, "critic")
    return _dashboard_payload(current_user, "critic")


@router.get("/moderator")
def moderator_dashboard(current_user: UserToken = Depends(get_current_user)):
    _enforce_role(current_user, "moderator")
    return _dashboard_payload(current_user, "moderator")


@router.get("/administrator")
def administrator_dashboard(current_user: UserToken = Depends(get_current_user)):
    _enforce_role(current_user, "administrator")
    return _dashboard_payload(current_user, "administrator")
