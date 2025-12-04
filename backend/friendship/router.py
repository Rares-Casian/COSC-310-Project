from fastapi import APIRouter, Depends, HTTPException
from backend.movies.utils import get_movie
from backend.authentication.security import get_current_user
from backend.authentication.schemas import UserToken
from backend.friendship.utils import (
    send_friend_request,
    accept_friend_request,
    get_pending_requests,
    get_friends,
    are_friends,
    get_user,
    get_user_by_username,
    remove_friend,
)

router = APIRouter(
    prefix="/friendship",
    tags=["Friendship"],
)


# --------------------------------------------------------
# Send friend request (by USERNAME)
# --------------------------------------------------------
@router.post("/request/{friend_username}")
def send_request_route(
    friend_username: str,
    current_user: UserToken = Depends(get_current_user),
):
    target = get_user_by_username(friend_username)
    if not target:
        raise HTTPException(404, "User not found")

    friend_id = target["user_id"]

    if current_user.user_id == friend_id:
        raise HTTPException(400, "You cannot friend yourself")

    if are_friends(current_user.user_id, friend_id):
        raise HTTPException(400, "You are already friends")

    ok = send_friend_request(current_user.user_id, friend_id)
    if not ok:
        raise HTTPException(400, "Request already exists or invalid")

    return {"message": "Friend request sent", "to": friend_username}


# --------------------------------------------------------
# List incoming friend requests (returns usernames)
# --------------------------------------------------------
@router.get("/requests")
def list_requests_route(
    current_user: UserToken = Depends(get_current_user),
):
    requester_ids = get_pending_requests(current_user.user_id)
    pending = []

    for rid in requester_ids:
        u = get_user(rid)
        if u:
            pending.append(
                {
                    "user_id": u["user_id"],
                    "username": u["username"],
                    "email": u["email"],
                }
            )

    return {"pending_requests": pending}


# --------------------------------------------------------
# Accept friend request (by SENDER USERNAME)
# --------------------------------------------------------
@router.post("/accept/{sender_username}")
def accept_request_route(
    sender_username: str,
    current_user: UserToken = Depends(get_current_user),
):
    sender = get_user_by_username(sender_username)
    if not sender:
        raise HTTPException(404, "User not found")

    sender_id = sender["user_id"]

    ok = accept_friend_request(current_user.user_id, sender_id)
    if not ok:
        raise HTTPException(404, "No such pending request")

    return {"message": "Friend request accepted", "friend_username": sender_username}


# --------------------------------------------------------
# Remove Friend (by USERNAME)
# --------------------------------------------------------
@router.delete("/remove/{friend_username}")
def remove_friend_route(
    friend_username: str,
    current_user: UserToken = Depends(get_current_user),
):
    friend = get_user_by_username(friend_username)
    if not friend:
        raise HTTPException(404, "User not found")

    friend_id = friend["user_id"]

    ok = remove_friend(current_user.user_id, friend_id)
    if not ok:
        raise HTTPException(404, "Friend not found")

    return {"message": "Friend removed", "friend_username": friend_username}


# --------------------------------------------------------
# List Friends (returns usernames)
# --------------------------------------------------------
@router.get("/list")
def list_friends_route(
    current_user: UserToken = Depends(get_current_user),
):
    friend_ids = get_friends(current_user.user_id)
    friends = []

    for fid in friend_ids:
        u = get_user(fid)
        if u:
            friends.append(
                {
                    "user_id": u["user_id"],
                    "username": u["username"],
                    "email": u["email"],
                }
            )

    return {"friends": friends}


# --------------------------------------------------------
# Friend Watchlist (by USERNAME)
# --------------------------------------------------------
@router.get("/{friend_username}/watchlist")
def friend_watchlist(friend_username: str, current_user: UserToken = Depends(get_current_user)):
    friend = get_user_by_username(friend_username)
    if not friend:
        raise HTTPException(404, "User not found")

    friend_id = friend["user_id"]

    if not are_friends(current_user.user_id, friend_id):
        raise HTTPException(403, "You are not friends")

    # Get movie IDs
    movie_ids = friend.get("watch_later", [])

    # Convert IDs → movie objects
    watchlist = []
    for m_id in movie_ids:
        movie = get_movie(m_id)
        if movie:
            watchlist.append(movie)

    return {
        "friend_username": friend_username,
        "watch_later": watchlist,
    }
