from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class Movie(BaseModel):
    movie_id: str
    title: str
    imdb_rating: Optional[float] = None
    meta_score: Optional[int] = None
    genres: List[str] = []
    directors: List[str] = []
    release_date: Optional[str] = None  # YYYY-MM-DD
    duration: Optional[int] = None  # minutes
    description: Optional[str] = None
    main_stars: List[str] = []
    total_user_reviews: Optional[int] = None
    total_critic_reviews: Optional[int] = None
    total_rating_count: Optional[int] = None


class MovieSearchParams(BaseModel):
    query: Optional[str] = Field(None, description="Free text search against title")
    genre: Optional[str] = None
    director: Optional[str] = None
    star: Optional[str] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    sort_by: str = "title"           # title|release_date|rating|meta_score|total_rating_count
    order: str = "asc"               # asc|desc
    page: int = 1
    limit: int = 20


class WatchLaterUpdate(BaseModel):
    movie_id: str
    action: str  # 'add' | 'remove'


class WatchLaterResponse(BaseModel):
    user_id: str
    watch_later: List[Movie]

