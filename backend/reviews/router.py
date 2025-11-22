"""Movie review creation, editing, deletion, and voting routes."""
from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from backend.reviews import utils, schemas
from backend.authentication.security import get_current_user, get_current_user_optional
from backend.authentication.schemas import TokenData
from backend.core.authz import block_if_penalized
from backend.core import exceptions

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/{movie_id}", response_model=List[schemas.Review])
def list_reviews(
    movie_id: str,
    rating: Optional[int] = Query(None, description="Filter by rating (1-10)"),
    sort_by: str = Query("date", description="Sort by date, rating, helpful, total_votes"),
    order: str = Query("desc", description="Order: asc or desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(get_current_user_optional)
):
    """List reviews for a movie with optional filtering, sorting, and pagination. Accessible to guests."""
    return utils.filter_sort_reviews(movie_id, rating, sort_by, order, skip, limit)


@router.get("/{movie_id}/{review_id}", response_model=schemas.Review)
def get_review(movie_id: str, review_id: str, current_user: TokenData = Depends(get_current_user_optional)):
    """Get a specific review by ID. Accessible to guests."""
    review = utils.get_review(movie_id, review_id)
    if not review:
        raise exceptions.NotFoundError("Review")
    return review



@router.post("/{movie_id}", response_model=schemas.Review)
@block_if_penalized(["review_ban", "posting_ban", "suspension"])
async def add_review(movie_id: str, review_data: schemas.ReviewCreate, current_user: TokenData = Depends(get_current_user)):
    """Add a new review for a movie; one review per user per movie. Requires authentication."""
    if current_user.role == "guest":
        raise exceptions.AuthenticationError("Authentication required to create reviews.")
    try:
        return utils.add_review(movie_id, review_data, current_user.user_id)
    except ValueError as e:
        raise exceptions.BusinessLogicError(str(e))



@router.patch("/{movie_id}/{review_id}", response_model=schemas.Review)
@block_if_penalized(["review_ban", "posting_ban", "suspension"])
async def edit_review(movie_id: str, review_id: str, updates: schemas.ReviewUpdate, current_user: TokenData = Depends(get_current_user)):
    """Edit a review; allowed for the author or an administrator. Requires authentication."""
    if current_user.role == "guest":
        raise exceptions.AuthenticationError("Authentication required to edit reviews.")
    review = utils.get_review(movie_id, review_id)
    if not review:
        raise exceptions.NotFoundError("Review")
    if review["user_id"] != current_user.user_id and current_user.role != "administrator":
        raise exceptions.AuthorizationError("Not authorized to edit this review.")
    return utils.update_review(movie_id, review_id, updates)


@router.delete("/{movie_id}/{review_id}")
def delete_review(movie_id: str, review_id: str, current_user: TokenData = Depends(get_current_user)):
    """Delete a review; allowed for the author, administrator, or moderator. Requires authentication."""
    if current_user.role == "guest":
        raise exceptions.AuthenticationError("Authentication required to delete reviews.")
    review = utils.get_review(movie_id, review_id)
    if not review:
        raise exceptions.NotFoundError("Review")
    if review["user_id"] != current_user.user_id and current_user.role not in ("administrator", "moderator"):
        raise exceptions.AuthorizationError("Not authorized to delete this review.")
    if not utils.delete_review(movie_id, review_id):
        raise exceptions.NotFoundError("Review")
    return {"message": "Review deleted successfully."}


@router.post("/{movie_id}/{review_id}/vote", response_model=schemas.Review)
@block_if_penalized(["suspension"])
def vote_review(movie_id: str, review_id: str, vote: schemas.Vote, current_user: TokenData = Depends(get_current_user)):
    """Vote whether a review was helpful or not. Requires authentication."""
    if current_user.role == "guest":
        raise exceptions.AuthenticationError("Authentication required to vote on reviews.")
    updated = utils.add_vote(movie_id, review_id, vote)
    if not updated:
        raise exceptions.NotFoundError("Review")
    return updated
