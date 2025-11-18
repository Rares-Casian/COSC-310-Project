"""
Schemas for review search and filtering.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid


class Usefulness(BaseModel):
    helpful: int = 0
    total_votes: int = 0


class Review(BaseModel):
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    movie_id: str
    user_id: str
    title: str
    rating: int
    date: str = Field(default_factory=lambda: datetime.utcnow().date().isoformat())
    text: str
    usefulness: Usefulness = Field(default_factory=Usefulness)


class ReviewCreate(BaseModel):
    title: str
    rating: int
    text: str


class ReviewUpdate(BaseModel):
    title: Optional[str] = None
    rating: Optional[int] = None
    text: Optional[str] = None


class Vote(BaseModel):
    vote: bool  # True = helpful, False = not helpful


class ReviewWithMetadata(Review):
    """Review with additional metadata for search results."""
    movie_title: Optional[str] = None
    critic_name: Optional[str] = None
    review_type: Literal["critic", "public"]


class ReviewSearchParams(BaseModel):
    """Parameters for searching/filtering."""
    query: Optional[str] = None  # Searches in title, critic name, and keywords (text)
    title: Optional[str] = None  # Search by review title
    critic_name: Optional[str] = None  # Search by critic name
    keywords: Optional[str] = None  # Search by keywords in review text
    review_type: Optional[Literal["critic", "public"]] = None  # Filter by review type
    movie_id: Optional[str] = None  # Filter by specific movie
    page: Optional[int] = 1
    limit: Optional[int] = 20


class ReviewSearchResponse(BaseModel):
    """Response for review search result."""
    total: int
    page: int
    limit: int
    results: List[ReviewWithMetadata]
