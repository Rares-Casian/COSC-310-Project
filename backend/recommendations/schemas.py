"""Recommendation schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional
from backend.movies.schemas import Movie


class RecommendedMovie(Movie):
    """Movie with recommendation metadata."""
    recommendation_reason: str = Field(..., description="Why this movie was recommended")
    recommendation_score: Optional[float] = Field(None, description="Recommendation confidence score (0-1)")


class RecommendationsResponse(BaseModel):
    """Response containing movie recommendations."""
    user_id: str
    recommendations: List[RecommendedMovie]
    recommendation_type: str = Field(..., description="Type of recommendation algorithm used")
    total_count: int


class RecommendationType(str):
    """Types of recommendation algorithms."""
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    FRIEND_BASED = "friend_based"
    POPULAR = "popular"
    HYBRID = "hybrid"

