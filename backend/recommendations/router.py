"""Recommendation API endpoints."""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from backend.authentication.security import get_current_user
from backend.authentication.schemas import UserToken
from backend.recommendations import utils, schemas
from backend.core.authz import require_role


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/", response_model=schemas.RecommendationsResponse)
def get_recommendations(
    recommendation_type: str = Query(
        "hybrid",
        description="Type of recommendation: content_based, collaborative, friend_based, popular, or hybrid"
    ),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of recommendations"),
    current_user: UserToken = Depends(get_current_user)
):
    """
    Get personalized movie recommendations for the current user.
    
    - **content_based**: Based on genres, directors, and stars you like
    - **collaborative**: Based on users with similar taste
    - **friend_based**: Based on what your friends liked
    - **popular**: Highly-rated and popular movies
    - **hybrid**: Combines all methods for best results
    """
    require_role(current_user, ["member", "critic", "moderator", "administrator"])
    
    rec_type = recommendation_type.lower()
    
    if rec_type == "content_based":
        recommendations = utils.content_based_recommendations(current_user.user_id, limit)
    elif rec_type == "collaborative":
        recommendations = utils.collaborative_recommendations(current_user.user_id, limit)
    elif rec_type == "friend_based":
        recommendations = utils.friend_based_recommendations(current_user.user_id, limit)
    elif rec_type == "popular":
        recommendations = utils.popular_recommendations(current_user.user_id, limit)
    else:  # Default to hybrid
        recommendations = utils.hybrid_recommendations(current_user.user_id, limit)
        rec_type = "hybrid"
    
    return schemas.RecommendationsResponse(
        user_id=current_user.user_id,
        recommendations=recommendations,
        recommendation_type=rec_type,
        total_count=len(recommendations)
    )

