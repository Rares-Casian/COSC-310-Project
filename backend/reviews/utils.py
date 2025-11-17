import os, json, tempfile, shutil
from typing import List, Dict, Optional
from datetime import datetime
from backend.reviews import schemas
from backend.authentication.utils import _convert_datetime_to_string, load_active_users, save_active_users

# Base directory for review JSON files
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "reviews")

#Return the full file path for storing reviews of a given movie.
#Ensures the base directory exists.
def _get_review_path(movie_id: str) -> str:
    os.makedirs(BASE_DIR, exist_ok=True)
    return os.path.join(BASE_DIR, f"{movie_id}_reviews.json")

#Load all reviews for a given movie from its JSON file.
def load_reviews(movie_id: str) -> List[Dict]:
    path = _get_review_path(movie_id)
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        print(f"[WARNING] Corrupted review file for movie {movie_id}. Resetting...")
        with open(path, "w") as f:
            json.dump([], f)
        return []


def save_reviews(movie_id: str, reviews: List[Dict]) -> None:
    """Safely write reviews to disk (atomic write)."""
    path = _get_review_path(movie_id)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path))
    os.close(tmp_fd)

    try:
        with open(tmp_path, "w") as f:
            json.dump(_convert_datetime_to_string(reviews), f, indent=2)
        shutil.move(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

#Check if a user has already submitted a review for a given movie.
def user_already_reviewed(movie_id: str, user_id: str) -> bool:
    users = load_active_users()
    for user in users:
        if user["user_id"] == user_id:
            return movie_id in user.get("movies_reviewed", [])
    return False