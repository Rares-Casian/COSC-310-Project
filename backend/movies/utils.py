# 🎬 Movies Utils — File-based operations for movies and watch-later features.
# ✅ Improved filter logic, added logging for invalid files, fixed rating filter direction.

import os, json, glob
from typing import List, Dict, Optional
from datetime import datetime
from backend.authentication.utils import _load_json, _save_json
from backend.reviews import utils as review_utils

MOVIES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "movies")
USERS_ACTIVE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users", "users_active.json")
REVIEWS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "reviews")


# score calculation for public/critic scores
def load_reviews_for_movie(movie_id: str) -> List[Dict]:
    """Load all reviews for a specific movie."""
    file_path = os.path.join(REVIEWS_DIR, f"{movie_id}_reviews.json")
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def calculate_critic_score(movie_id: str) -> Optional[float]:
    reviews = load_reviews_for_movie(movie_id)
    if not reviews:
        return None
    
    critic_ratings = []
    for review in reviews:
        if review_utils.is_critic_review(review):
            rating = review.get("rating")
            if rating is not None and 0 <= rating <= 10:
                critic_ratings.append(rating)
    
    if not critic_ratings:
        return None
    
    return round(sum(critic_ratings) / len(critic_ratings), 2)


def calculate_public_score(movie_id: str) -> Optional[float]:
    reviews = load_reviews_for_movie(movie_id)
    if not reviews:
        return None
    
    public_ratings = []
    for review in reviews:
        if not review_utils.is_critic_review(review):
            rating = review.get("rating")
            if rating is not None and 0 <= rating <= 10:
                public_ratings.append(rating)
    
    if not public_ratings:
        return None
    
    return round(sum(public_ratings) / len(public_ratings), 2)


def enrich_movie_with_scores(movie: Dict) -> Dict:
    enriched = movie.copy()
    movie_id = movie.get("movie_id")
    
    if movie_id:
        critic_score = calculate_critic_score(movie_id)
        public_score = calculate_public_score(movie_id)
        enriched["critic_score"] = critic_score
        enriched["public_score"] = public_score
    
    return enriched



# ---------- MOVIE OPERATIONS ----------
def load_movies() -> List[Dict]:
    """Load all movies from data/movies/ folder."""
    movies = []
    for file in glob.glob(os.path.join(MOVIES_DIR, "*.json")):
        try:
            with open(file, "r") as f:
                movie = json.load(f)
                movies.append(movie)
        except json.JSONDecodeError as e:
            #  log invalid JSON instead of silently skipping
            print(f"[WARN] Skipping invalid movie file {file}: {e}")
    return movies


def get_movie(movie_id: str) -> Optional[Dict]:
    """Return single movie by ID."""
    path = os.path.join(MOVIES_DIR, f"{movie_id}.json")
    if not os.path.exists(path):
        return None
    return _load_json(path)
    movie = _load_json(path)
    if movie:
        movie = enrich_movie_with_scores(movie)
    return movie


def _parse_year(date_str: Optional[str]) -> Optional[int]:
    """Extract year from YYYY-MM-DD string."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").year
    except Exception:
        return None


def filter_movies(movies: List[Dict], params) -> List[Dict]:
    """Apply search and filtering logic."""
    filtered = []
    for m in movies:
        year = _parse_year(m.get("release_date"))

        if params.query and params.query.lower() not in m["title"].lower():
            continue
        if params.genre and params.genre.lower() not in [g.lower() for g in m.get("genres", [])]:
            continue
        if params.director and params.director.lower() not in [d.lower() for d in m.get("directors", [])]:
            continue
        if params.star and not any(params.star.lower() in s.lower() for s in m.get("main_stars", [])):
            continue

        # Corrected max_rating comparison direction
        if params.min_rating and (m.get("imdb_rating") or 0) < params.min_rating:
            continue
        if params.max_rating and (m.get("imdb_rating") or 10) > params.max_rating:
            continue
        if params.min_year and (year or 0) < params.min_year:
            continue
        if params.max_year and (year or 9999) > params.max_year:
            continue

        filtered.append(m)
    return filtered


def sort_movies(movies: List[Dict], sort_by: str, order: str) -> List[Dict]:
    """Sort by supported fields."""
    reverse = order.lower() == "desc"
    key = sort_by.lower()

    def sort_key(m):
        if key == "title":
            return m.get("title", "")
        if key == "release_date":
            return m.get("release_date", "")
        if key in ("rating", "imdb_rating"):
            return m.get("imdb_rating") or 0
        if key == "meta_score":
            return m.get("meta_score") or 0
        if key == "total_rating_count":
            return m.get("total_rating_count") or 0
        return 0

    return sorted(movies, key=sort_key, reverse=reverse)


def paginate_movies(movies: List[Dict], page: int, limit: int) -> List[Dict]:
    start = (page - 1) * limit
    end = start + limit
    return movies[start:end]


# ---------- WATCH LATER ----------
def _load_users() -> list:
    return _load_json(USERS_ACTIVE_FILE)

def _save_users(data: list) -> None:
    _save_json(USERS_ACTIVE_FILE, data)

def _find_user(user_id: str, users: list) -> Optional[Dict]:
    for u in users:
        if u["user_id"] == user_id:
            return u
    return None

def get_watch_later(user_id: str) -> List[Dict]:
    users = _load_users()
    user = _find_user(user_id, users)
    if not user:
        return []
    movie_ids = user.get("watch_later", [])
    all_movies = load_movies()
    return [m for m in all_movies if m["movie_id"] in movie_ids]

def update_watch_later(user_id: str, movie_id: str, action: str) -> None:
    users = _load_users()
    user = _find_user(user_id, users)
    if not user:
        return
    wl = user.get("watch_later", [])
    if action == "add" and movie_id not in wl:
        wl.append(movie_id)
    elif action == "remove" and movie_id in wl:
        wl.remove(movie_id)
    user["watch_later"] = wl
    _save_users(users)
