
import os, json
from typing import List, Optional
from datetime import datetime
from backend.penalties import schemas
from backend.authentication import utils as user_utils

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'penalties')
os.makedirs(BASE_DIR, exist_ok=True)
PENALTIES_FILE = os.path.join(BASE_DIR, 'penalties.json')

def _load_penalties() -> List[dict]:
    if not os.path.exists(PENALTIES_FILE):
        return []
    with open(PENALTIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_penalties(data: List[dict]):
    with open(PENALTIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def add_penalty(penalty: schemas.Penalty) -> schemas.Penalty:
    data = _load_penalties()
    data.append(penalty.dict())
    _save_penalties(data)

    users = user_utils.load_active_users()
    for u in users:
        if u["user_id"] == penalty.user_id:
            u.setdefault("penalties", []).append(penalty.penalty_id)
            user_utils.save_active_users(users)
            break

    return penalty


def get_penalties_for_user(user_id: str) -> List[schemas.Penalty]:
    penalties = [schemas.Penalty(**p) for p in _load_penalties() if p["user_id"] == user_id]
    changed = False
    all_penalties = _load_penalties()

    for p in penalties:
        if p.status == "active" and p.has_expired():
            p.status = "expired"
            changed = True
            for stored in all_penalties:
                if stored["penalty_id"] == p.penalty_id:
                    stored["status"] = "expired"

            _unlink_penalty_from_user(p.user_id, p.penalty_id)

    if changed:
        _save_penalties(all_penalties)

    return penalties


def resolve_penalty(penalty_id: str, moderator_id: str, notes: Optional[str] = None):
    data = _load_penalties()
    target_user_id = None

    for p in data:
        if p["penalty_id"] == penalty_id:
            p["status"] = "resolved"
            p["notes"] = notes
            p["resolved_by"] = moderator_id
            p["resolved_at"] = datetime.utcnow().isoformat()
            target_user_id = p["user_id"]
            break

    _save_penalties(data)

    if target_user_id:
        _unlink_penalty_from_user(target_user_id, penalty_id)


def delete_penalty(penalty_id: str):
    data = _load_penalties()
    target_user_id = None

    for p in data:
        if p["penalty_id"] == penalty_id:
            target_user_id = p["user_id"]
            break

    updated = [p for p in data if p["penalty_id"] != penalty_id]
    _save_penalties(updated)

    if target_user_id:
        _unlink_penalty_from_user(target_user_id, penalty_id)


def _unlink_penalty_from_user(user_id: str, penalty_id: str):
    users = user_utils.load_active_users()
    for user in users:
        if user["user_id"] == user_id and "penalties" in user:
            if penalty_id in user["penalties"]:
                user["penalties"].remove(penalty_id)
                user_utils.save_active_users(users)
            break


def check_active_penalty(user_id: str, blocked_types: List[str]) -> Optional[str]:
    penalties = get_penalties_for_user(user_id)
    for p in penalties:
        if p.status == "active" and p.type in blocked_types:
            remaining = p.time_remaining or "Unknown duration"
            return f"Action blocked due to active {p.type} ({p.reason}) — {remaining}."
    return None
