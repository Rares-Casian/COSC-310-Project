"""Review storage and user linkage utilities."""
import os, glob, uuid
from datetime import datetime
from typing import List, Dict, Optional
from backend.core.paths import REVIEWS_DIR
from backend.core.jsonio import load_json, save_json, ensure_parent
from backend.authentication.utils import load_active_users, save_active_users
from backend.reviews import schemas


def _path(movie_id: str) -> str:
    ensure_parent(os.path.join(REVIEWS_DIR, "placeholder"))
    return os.path.join(REVIEWS_DIR, f"{movie_id}_reviews.json")


def load_reviews(movie_id: str) -> List[Dict]:
    return load_json(_path(movie_id), default=[])


def save_reviews(movie_id: str, reviews: List[Dict]) -> None:
    save_json(_path(movie_id), reviews, atomic=True)


def user_already_reviewed(movie_id: str, user_id: str) -> bool:
    """Check if the user already has a review for the movie."""
    users = load_active_users()
    for u in users:
        if u.get("user_id") == user_id:
            return movie_id in u.get("movies_reviewed", [])
    return False

def is_critic_review(review: Dict) -> bool:
    """Check if a review is from a critic by checking the user's role."""
    user_id = review.get("user_id", "")
    if not user_id:
        return False
    
    users = load_active_users()
    for u in users:
        if u.get("user_id") == user_id:
            return u.get("role", "").lower() == "critic"
    return False

def add_review(movie_id: str, review_data, user_id: str):
    """Add a new review for a movie; ensures unique ID and timestamp."""
    reviews = load_reviews(movie_id)

    # Prevent duplicate by same user
    if any(r.get("user_id") == user_id for r in reviews):
        raise ValueError("User already has a review for this movie.")

    new_review = {
        "review_id": str(uuid.uuid4()),
        "movie_id": movie_id,
        "user_id": user_id,
        "title": review_data.title,
        "rating": review_data.rating,
        "text": review_data.text,
        "date": datetime.utcnow().date().isoformat(),
        "usefulness": {"helpful": 0, "total_votes": 0},
    }

    reviews.append(new_review)
    save_reviews(movie_id, reviews)

    # Optionally add the movie_id to user's movies_reviewed
    from backend.authentication import utils as user_utils
    users = user_utils.load_active_users()
    for u in users:
        if u["user_id"] == user_id:
            u.setdefault("movies_reviewed", [])
            if movie_id not in u["movies_reviewed"]:
                u["movies_reviewed"].append(movie_id)
    user_utils.save_active_users(users)

    return new_review


def get_review(movie_id: str, review_id: str) -> Optional[Dict]:
    return next((r for r in load_reviews(movie_id) if r.get("review_id") == review_id), None)


def update_review(movie_id: str, review_id: str, updates: schemas.ReviewUpdate) -> Optional[Dict]:
    reviews = load_reviews(movie_id)
    for r in reviews:
        if r.get("review_id") == review_id:
            for k, v in updates.dict(exclude_unset=True).items():
                r[k] = v
            r["date"] = datetime.utcnow().date().isoformat()
            save_reviews(movie_id, reviews)
            return r
    return None


def delete_review(movie_id: str, review_id: str) -> bool:
    reviews = load_reviews(movie_id)
    updated = [r for r in reviews if r.get("review_id") != review_id]
    if len(updated) == len(reviews):
        return False
    save_reviews(movie_id, updated)
    return True


def add_vote(movie_id: str, review_id: str, vote: schemas.Vote) -> Optional[Dict]:
    reviews = load_reviews(movie_id)
    for r in reviews:
        if r.get("review_id") == review_id:
            r.setdefault("usefulness", {"helpful": 0, "total_votes": 0})
            r["usefulness"]["total_votes"] += 1
            if vote.vote:
                r["usefulness"]["helpful"] += 1
            save_reviews(movie_id, reviews)
            return r
    return None


def filter_sort_reviews(
    movie_id: str,
    rating: Optional[int] = None,
    sort_by: str = "date",
    order: str = "desc",
    skip: int = 0,
    limit: int = 20,
) -> List[Dict]:
    """Filter and sort reviews for a movie."""
    reviews = load_reviews(movie_id)
    if rating is not None:
        reviews = [r for r in reviews if r.get("rating") == rating]

    reverse = order.lower() == "desc"
    if sort_by in {"date", "rating"}:
        reviews.sort(key=lambda r: r.get(sort_by), reverse=reverse)
    elif sort_by == "helpful":
        reviews.sort(key=lambda r: r.get("usefulness", {}).get("helpful", 0), reverse=reverse)
    elif sort_by == "total_votes":
        reviews.sort(key=lambda r: r.get("usefulness", {}).get("total_votes", 0), reverse=reverse)

    return reviews[skip: skip + limit]


def get_reviews_by_user(user_id: str) -> List[Dict]:
    """Return all reviews by a specific user across all movies."""
    out: List[Dict] = []
    for path in glob.glob(os.path.join(REVIEWS_DIR, "*_reviews.json")):
        out.extend([r for r in load_json(path, default=[]) if r.get("user_id") == user_id])
    return out
