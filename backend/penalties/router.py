"""Penalty management routes for administrators and moderators."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from backend.penalties import utils, schemas
from backend.authentication.security import get_current_user
from backend.core.authz import require_role

router = APIRouter(prefix="/penalties", tags=["Penalties"])


@router.get("/", response_model=List[schemas.Penalty])
def list_all_penalties(current_user=Depends(get_current_user)):
    require_role(current_user, ["administrator", "moderator"])
    return [schemas.Penalty(**p) for p in utils._load()]


@router.get("/me", response_model=List[schemas.Penalty])
def get_my_penalties(current_user=Depends(get_current_user)):
    return utils.get_penalties_for_user(current_user.user_id)


@router.get("/{user_id}", response_model=List[schemas.Penalty])
def get_user_penalties(user_id: str, current_user=Depends(get_current_user)):
    require_role(current_user, ["administrator", "moderator"])
    return utils.get_penalties_for_user(user_id)


@router.post("/", response_model=schemas.Penalty)
def issue_penalty(payload: schemas.PenaltyCreate, current_user=Depends(get_current_user)):
    require_role(current_user, ["administrator", "moderator"])
    expires_at = schemas.calculate_expiry(payload.type, payload.severity, payload.duration_days)

    penalty = schemas.Penalty(
        penalty_id=str(uuid.uuid4()), 
        user_id=payload.user_id,
        type=payload.type,
        severity=payload.severity,
        reason=payload.reason,
        issued_by=current_user.user_id,
        expires_at=expires_at,
    )

    return utils.add_penalty(penalty)


@router.patch("/{penalty_id}")
def resolve_penalty(penalty_id: str, notes: Optional[str] = Query(None), current_user=Depends(get_current_user)):
    require_role(current_user, ["administrator", "moderator"])
    utils.resolve_penalty(penalty_id, moderator_id=current_user.user_id, notes=notes)
    return {"message": f"Penalty {penalty_id} resolved successfully."}


@router.delete("/{penalty_id}")
def delete_penalty(penalty_id: str, current_user=Depends(get_current_user)):
    require_role(current_user, ["administrator"])
    data = utils._load()
    if not any(p.get("penalty_id") == penalty_id for p in data):
        raise HTTPException(status_code=404, detail="Penalty not found.")
    utils.delete_penalty(penalty_id)
    return {"message": f"Penalty {penalty_id} deleted successfully."}
