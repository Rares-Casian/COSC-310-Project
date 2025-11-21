"""Movie catalog + watch-later list management."""
import os, glob
from typing import List, Dict, Optional
from datetime import datetime
from backend.core.paths import MOVIES_DIR, USERS_ACTIVE_FILE
from backend.core.jsonio import load_json, save_json


def load_movies() -> List[Dict]:
    """Load all movie JSON files."""
    movies = []
    for path in glob.glob(os.path.join(MOVIES_DIR, "*.json")):
        m = load_json(path, default=None)
        if isinstance(m, dict):
            movies.append(m)
    return movies


def get_movie(movie_id: str) -> Optional[Dict]:
    path = os.path.join(MOVIES_DIR, f"{movie_id}.json")
    doc = load_json(path, default=None)
    return doc if isinstance(doc, dict) else None


def _parse_year(date_str: Optional[str]) -> Optional[int]:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").year
    except Exception:
        return None


def filter_movies(movies: List[Dict], params) -> List[Dict]:
    """Filter and search movies by parameters."""
    out = []
    for m in movies:
        year = _parse_year(m.get("release_date"))
        if getattr(params, "query", None) and getattr(params, "query").lower() not in m.get("title", "").lower():
            continue
        if getattr(params, "genre", None) and getattr(params, "genre").lower() not in [g.lower() for g in m.get("genres", [])]:
            continue
        if getattr(params, "director", None) and getattr(params, "director").lower() not in [d.lower() for d in m.get("directors", [])]:
            continue
        rating = m.get("imdb_rating") or 0
        if getattr(params, "min_rating", None) and rating < params.min_rating:
            continue
        if getattr(params, "max_rating", None) and rating > params.max_rating:
            continue
        if getattr(params, "min_year", None) and (year or 0) < params.min_year:
            continue
        if getattr(params, "max_year", None) and (year or 9999) > params.max_year:
            continue
        out.append(m)
    return out


def sort_movies(movies: List[Dict], sort_by: str, order: str) -> List[Dict]:
    reverse = order.lower() == "desc"
    key = sort_by.lower()

    def _k(m: Dict):
        if key == "title":
            return m.get("title", "")
        if key == "release_date":
            return m.get("release_date", "")
        if key in ("rating", "imdb_rating"):
            return m.get("imdb_rating") or 0
        if key == "meta_score":
            return m.get("meta_score") or 0
        return 0

    return sorted(movies, key=_k, reverse=reverse)


def paginate_movies(movies: List[Dict], page: int, limit: int) -> List[Dict]:
    start = max(page - 1, 0) * max(limit, 1)
    end = start + max(limit, 1)
    return movies[start:end]


# ---- Watch later ----

def _load_users() -> List[Dict]:
    return load_json(USERS_ACTIVE_FILE, default=[])


def _save_users(data: List[Dict]) -> None:
    save_json(USERS_ACTIVE_FILE, data)


def get_watch_later(user_id: str) -> List[Dict]:
    users = _load_users()
    user = next((u for u in users if u.get("user_id") == user_id), None)
    if not user:
        return []
    movie_ids = user.get("watch_later", [])
    all_movies = load_movies()
    return [m for m in all_movies if m.get("movie_id") in movie_ids]


def update_watch_later(user_id: str, movie_id: str, action: str) -> None:
    users = _load_users()
    user = next((u for u in users if u.get("user_id") == user_id), None)
    if not user:
        return
    wl = list(user.get("watch_later", []))
    if action == "add" and movie_id not in wl:
        wl.append(movie_id)
    elif action == "remove" and movie_id in wl:
        wl.remove(movie_id)
    user["watch_later"] = wl
    _save_users(users)
