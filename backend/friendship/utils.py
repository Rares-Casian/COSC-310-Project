"""Friendship utilities working directly on users_active.json."""
from typing import List, Dict, Optional
from backend.core.jsonio import load_json, save_json
from backend.core.paths import USERS_ACTIVE_FILE


# ----------------------------------------
# Internal user load/save
# ----------------------------------------

def _load_users() -> List[Dict]:
    return load_json(USERS_ACTIVE_FILE, default=[])


def _save_users(data: List[Dict]) -> None:
    save_json(USERS_ACTIVE_FILE, data)


# ----------------------------------------
# Core helpers
# ----------------------------------------

def get_user(user_id: str) -> Optional[Dict]:
    users = _load_users()
    return next((u for u in users if u["user_id"] == user_id), None)


def are_friends(user_a: str, user_b: str) -> bool:
    """Check if two users are mutual friends."""
    u = get_user(user_a)
    return u is not None and user_b in u.get("friends", [])


def _mutual_add_friends(user_id: str, friend_id: str) -> bool:
    """Internal: mutually add each user to the other's friends list."""
    users = _load_users()
    u = next((x for x in users if x["user_id"] == user_id), None)
    f = next((x for x in users if x["user_id"] == friend_id), None)

    if not u or not f:
        return False

    u.setdefault("friends", [])
    f.setdefault("friends", [])

    if friend_id not in u["friends"]:
        u["friends"].append(friend_id)

    if user_id not in f["friends"]:
        f["friends"].append(user_id)

    _save_users(users)
    return True


def remove_friend(user_id: str, friend_id: str) -> bool:
    """Mutually remove each other from friends list."""
    users = _load_users()
    u = next((x for x in users if x["user_id"] == user_id), None)
    f = next((x for x in users if x["user_id"] == friend_id), None)

    if not u or not f:
        return False

    u["friends"] = [x for x in u.get("friends", []) if x != friend_id]
    f["friends"] = [x for x in f.get("friends", []) if x != user_id]

    _save_users(users)
    return True


def get_friends(user_id: str) -> List[str]:
    """Return a list of friend IDs for a user."""
    u = get_user(user_id)
    return u.get("friends", []) if u else []

def get_user_by_username(username: str) -> Optional[Dict]:
    """Find a user by their unique username."""
    users = _load_users()
    return next((u for u in users if u["username"] == username), None)


# ----------------------------------------
# Friend request logic
# ----------------------------------------

def send_friend_request(sender_id: str, receiver_id: str) -> bool:
    """Add a friend request to receiver's 'friend_requests' list."""
    users = _load_users()
    sender = next((x for x in users if x["user_id"] == sender_id), None)
    receiver = next((x for x in users if x["user_id"] == receiver_id), None)

    if not sender or not receiver:
        return False

    # Don't allow if already friends
    if receiver_id in sender.get("friends", []) or sender_id in receiver.get("friends", []):
        return False

    # Don't duplicate requests
    receiver.setdefault("friend_requests", [])
    if sender_id in receiver["friend_requests"]:
        return False

    receiver["friend_requests"].append(sender_id)
    _save_users(users)
    return True


def get_pending_requests(user_id: str) -> List[str]:
    """Return a list of user_ids who sent a friend request to this user."""
    u = get_user(user_id)
    return u.get("friend_requests", []) if u else []


def accept_friend_request(receiver_id: str, sender_id: str) -> bool:
    """
    Accept a friend request:
    - Remove sender_id from receiver.friend_requests
    - Add each to the other's friends list.
    """
    users = _load_users()
    receiver = next((x for x in users if x["user_id"] == receiver_id), None)
    sender = next((x for x in users if x["user_id"] == sender_id), None)

    if not receiver or not sender:
        return False

    requests = receiver.get("friend_requests", [])
    if sender_id not in requests:
        return False

    # Remove request
    receiver["friend_requests"] = [x for x in requests if x != sender_id]

    # Mutual add
    receiver.setdefault("friends", [])
    sender.setdefault("friends", [])

    if sender_id not in receiver["friends"]:
        receiver["friends"].append(sender_id)
    if receiver_id not in sender["friends"]:
        sender["friends"].append(receiver_id)

    _save_users(users)
    return True
