"""Utility functions for managing reviews stored in JSON files."""

import os
import json
from typing import List, Dict, Optional
from backend.users import utils as user_utils


# file paths
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REVIEWS_DIR = os.path.join(BASE_DIR, "reviews")
MOVIES_DIR = os.path.join(BASE_DIR, "movies")


def _load_json(path: str) -> List[Dict]:

    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _load_json_file(filename: str, directory: str) -> Dict:
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_all_reviews() -> List[Dict]:
    """Load all reviews from all movie review files."""
    all_reviews = []
    
    if not os.path.exists(REVIEWS_DIR):
        return all_reviews
    
    for filename in os.listdir(REVIEWS_DIR):
        if filename.endswith("_reviews.json"):
            file_path = os.path.join(REVIEWS_DIR, filename)
            reviews = _load_json(file_path)
            all_reviews.extend(reviews)
    
    return all_reviews


def get_movie_by_id(movie_id: str) -> Optional[Dict]:
    """Get a movie by its ID."""
    return _load_json_file(f"{movie_id}.json", MOVIES_DIR)


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get a user by their ID."""
    return user_utils.get_user_by_id(user_id)


def is_critic_review(review: Dict) -> bool:
    """Check if a review is from a critic."""
    user = get_user_by_id(review.get("user_id", ""))
    if not user:
        return False
    return user.get("role", "").lower() == "critic"


def enrich_review(review: Dict) -> Dict:
    """Enrich a review with metadata (movie title, critic name, review type)."""
    enriched = review.copy()
    
    # Get movie title
    movie = get_movie_by_id(review.get("movie_id", ""))
    enriched["movie_title"] = movie.get("title", "") if movie else None
    
    # Get critic name and determine review type
    user = get_user_by_id(review.get("user_id", ""))
    if user:
        enriched["critic_name"] = user.get("username", "")
        enriched["review_type"] = "critic" if user.get("role", "").lower() == "critic" else "public"
    else:
        enriched["critic_name"] = None
        enriched["review_type"] = "public"  # Defaults to public if user not found
    
    return enriched


def search_reviews(
    query: Optional[str] = None,
    title: Optional[str] = None,
    critic_name: Optional[str] = None,
    keywords: Optional[str] = None,
    review_type: Optional[str] = None,
    movie_id: Optional[str] = None,
) -> List[Dict]:
   
    all_reviews = load_all_reviews()
    enriched_reviews = [enrich_review(r) for r in all_reviews]
    
    filtered_reviews = enriched_reviews
    
    # Filter by movie id first
    if movie_id:
        filtered_reviews = [r for r in filtered_reviews if r.get("movie_id") == movie_id]
    
    # Filter by review type
    if review_type:
        filtered_reviews = [r for r in filtered_reviews if r.get("review_type") == review_type]
    
    # Search by review title
    if title:
        title_lower = title.lower()
        filtered_reviews = [
            r for r in filtered_reviews
            if title_lower in r.get("title", "").lower()
        ]
    
    # Search by critic name
    if critic_name:
        critic_lower = critic_name.lower()
        filtered_reviews = [
            r for r in filtered_reviews
            if r.get("critic_name") and critic_lower in r.get("critic_name", "").lower()
        ]
    
    # Search by keywords in review
    if keywords:
        keywords_lower = keywords.lower()
        filtered_reviews = [
            r for r in filtered_reviews
            if keywords_lower in r.get("text", "").lower()
        ]
    
    # General query search
    if query:
        query_lower = query.lower()
        filtered_reviews = [
            r for r in filtered_reviews
            if (
                query_lower in r.get("title", "").lower()
                or (r.get("critic_name") and query_lower in r.get("critic_name", "").lower())
                or query_lower in r.get("text", "").lower()
            )
        ]
    
    return filtered_reviews

