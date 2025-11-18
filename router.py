"""Handles review search and filtering functionality."""

from fastapi import APIRouter, Query
from typing import Optional
from backend.reviews import schemas, utils

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/search", response_model=schemas.ReviewSearchResponse)
def search_reviews(
    query: Optional[str] = Query(None, description="General search query (searches in title, critic name, and text)"),
    title: Optional[str] = Query(None, description="Search by review title"),
    critic_name: Optional[str] = Query(None, description="Search by critic name"),
    keywords: Optional[str] = Query(None, description="Search by keywords in review"),
    review_type: Optional[str] = Query(None, description="Filter by review type: 'critic' or 'public'"),
    movie_id: Optional[str] = Query(None, description="Filter by movie ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
):
   
    # Validate review type
    if review_type and review_type not in ["critic", "public"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="review_type must be 'critic' or 'public'")
    
    # Perform search
    results = utils.search_reviews(
        query=query,
        title=title,
        critic_name=critic_name,
        keywords=keywords,
        review_type=review_type,
        movie_id=movie_id,
    )
    
    # pagination
    total = len(results)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_results = results[start_idx:end_idx]
    
    return schemas.ReviewSearchResponse(
        total=total,
        page=page,
        limit=limit,
        results=paginated_results
    )

