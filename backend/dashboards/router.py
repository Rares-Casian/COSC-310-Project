"""Role-specific dashboard endpoints."""
from fastapi import APIRouter, Depends
from typing import Dict, List

from backend.authentication.security import get_current_user
from backend.authentication.schemas import UserToken
from backend.users import utils as user_utils
from backend.core import exceptions

# Explicitly include in schema so the docs always show these routes.
router = APIRouter(prefix="/dashboard", tags=["Dashboard"], include_in_schema=True)


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

ROLE_ALIASES = {
    "admin": "administrator",
    "admins": "administrator",
}


def _normalize_role(role: str) -> str:
    normalized = ROLE_ALIASES.get(role, role)
    return normalized


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
            {"label": "Watchlist", "href": "/movies/watch-later"},
            {"label": "Reviews", "href": "/reviews"},
        ],
    }


def _enforce_role(current_user: UserToken, required_role: str):
    normalized_current = _normalize_role(current_user.role)
    normalized_required = _normalize_role(required_role)
    if normalized_current != normalized_required:
        raise exceptions.AuthorizationError(f"Access denied: requires role '{normalized_required}'.")


@router.get("/guest")
def guest_dashboard(current_user: UserToken = Depends(get_current_user)):
    normalized_role = "guest"
    _enforce_role(current_user, normalized_role)
    return _dashboard_payload(current_user, normalized_role)


@router.get("/member")
def member_dashboard(current_user: UserToken = Depends(get_current_user)):
    normalized_role = "member"
    _enforce_role(current_user, normalized_role)
    return _dashboard_payload(current_user, normalized_role)


@router.get("/critic")
def critic_dashboard(current_user: UserToken = Depends(get_current_user)):
    normalized_role = "critic"
    _enforce_role(current_user, normalized_role)
    return _dashboard_payload(current_user, normalized_role)


@router.get("/moderator")
def moderator_dashboard(current_user: UserToken = Depends(get_current_user)):
    normalized_role = "moderator"
    _enforce_role(current_user, normalized_role)
    return _dashboard_payload(current_user, normalized_role)


@router.get("/administrator")
def administrator_dashboard(current_user: UserToken = Depends(get_current_user)):
    normalized_role = "administrator"
    _enforce_role(current_user, normalized_role)
    return _dashboard_payload(current_user, normalized_role)
