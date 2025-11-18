"""Penalties CRUD operations with user linkage."""
from datetime import datetime
from typing import List, Optional
from backend.core.paths import PENALTIES_FILE
from backend.core.jsonio import load_json, save_json
from backend.penalties import schemas
from backend.authentication import utils as user_utils


def _load() -> List[dict]:
    return load_json(PENALTIES_FILE, default=[])


def _save(data: List[dict]) -> None:
    save_json(PENALTIES_FILE, data)


def add_penalty(penalty: schemas.Penalty) -> schemas.Penalty:
    data = _load()
    data.append(penalty.dict())
    _save(data)

    users = user_utils.load_active_users()
    for u in users:
        if u.get("user_id") == penalty.user_id:
            u.setdefault("penalties", []).append(penalty.penalty_id)
            user_utils.save_active_users(users)
            break
    return penalty


def _unlink_penalty_from_user(user_id: str, penalty_id: str) -> None:
    users = user_utils.load_active_users()
    for u in users:
        if u.get("user_id") == user_id and "penalties" in u:
            if penalty_id in u["penalties"]:
                u["penalties"].remove(penalty_id)
                user_utils.save_active_users(users)
            break


def get_penalties_for_user(user_id: str) -> List[schemas.Penalty]:
    penalties = [schemas.Penalty(**p) for p in _load() if p.get("user_id") == user_id]
    changed = False
    all_pen = _load()

    for p in penalties:
        if p.status == "active" and p.has_expired():
            p.status = "expired"
            changed = True
            for stored in all_pen:
                if stored.get("penalty_id") == p.penalty_id:
                    stored["status"] = "expired"
            _unlink_penalty_from_user(p.user_id, p.penalty_id)

    if changed:
        _save(all_pen)
    return penalties


# Alias for dashboards expecting this name
get_penalties_by_user = get_penalties_for_user


def resolve_penalty(penalty_id: str, moderator_id: str, notes: Optional[str] = None) -> None:
    data = _load()
    tgt_user = None
    for p in data:
        if p.get("penalty_id") == penalty_id:
            p["status"] = "resolved"
            p["notes"] = notes
            p["resolved_by"] = moderator_id
            p["resolved_at"] = datetime.utcnow().isoformat()
            tgt_user = p.get("user_id")
            break
    _save(data)
    if tgt_user:
        _unlink_penalty_from_user(tgt_user, penalty_id)


def delete_penalty(penalty_id: str) -> None:
    data = _load()
    tgt_user = None
    for p in data:
        if p.get("penalty_id") == penalty_id:
            tgt_user = p.get("user_id")
            break
    updated = [p for p in data if p.get("penalty_id") != penalty_id]
    _save(updated)
    if tgt_user:
        _unlink_penalty_from_user(tgt_user, penalty_id)


def check_active_penalty(user_id: str, blocked_types: list[str]) -> str | None:
    penalties = _load()
    for p in penalties:
        if p["user_id"] == user_id and p["status"] == "active" and p["type"] in blocked_types:
            return f"User has an active {p['type']} penalty"
    return None

