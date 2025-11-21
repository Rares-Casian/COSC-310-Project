# Movies Router — Handles all movie browsing and watch-later features.



"""Movie browsing and watch-later list routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
import tempfile, os
from backend.authentication.security import get_current_user
from backend.authentication.schemas import UserToken
from backend.movies import utils, schemas
from backend.core.authz import require_role, block_if_penalized
from backend.core.jsonio import save_json

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=List[schemas.Movie])
def list_movies(params: schemas.MovieSearchParams = Depends(), current_user: UserToken = Depends(get_current_user)):
    """List, search, sort, and paginate movies."""
    movies = utils.load_movies()
    movies = utils.filter_movies(movies, params)
    movies = utils.sort_movies(movies, params.sort_by, params.order)
    return utils.paginate_movies(movies, params.page, params.limit)


@router.get("/download")
def download_movies(background_tasks: BackgroundTasks, current_user: UserToken = Depends(get_current_user)):
    """Download all movies as a single JSON file (admin only)."""
    require_role(current_user, ["administrator"])
    movies = utils.load_movies()
    if not movies:
        raise NotFoundError("No movies found.")

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    save_json(tmp_file.name, movies)
    background_tasks.add_task(os.remove, tmp_file.name)
    return FileResponse(tmp_file.name, filename="movies.json", media_type="application/json")


@router.get("/watch-later", response_model=schemas.WatchLaterResponse)
def get_watch_later(
    current_user: schemas.UserToken = Depends(get_current_user),
    user_id: Optional[str] = Query(None, description="Admin can specify another user ID")
):
    """
    Regular users → view their own watch-later list.
    Admins → can view any user's watch-later list by passing ?user_id=<target_id>.
    """
    target_id = current_user.user_id

    if user_id:
        if current_user.role != "administrator":
            raise ForbiddenError("Not authorized to view other users' lists.")
        target_id = user_id

    movies = utils.get_watch_later(target_id)
    return {"user_id": target_id, "watch_later": movies}


@router.patch("/watch-later")
def modify_watch_later(
    update: schemas.WatchLaterUpdate,
    current_user: schemas.UserToken = Depends(get_current_user),
    user_id: Optional[str] = Query(None, description="Admin can modify another user’s list")
):
    """
    Regular users → can only modify their own watch-later.
    Admins → can modify another user's list using ?user_id=<target_id>.
    Restricted by penalties:
    - suspension
    """
    # Check for suspension
    restriction = penalty_utils.check_active_penalty(current_user.user_id, ["suspension"])
    if restriction:
        raise ForbiddenError(restriction)

    # Validate action
@block_if_penalized(["suspension"])
async def modify_watch_later(update: schemas.WatchLaterUpdate, current_user: UserToken = Depends(get_current_user), user_id: Optional[str] = Query(None)):
    """Add or remove movies from watch-later list. Admin may target another user."""
    if update.action not in ["add", "remove"]:
        raise ValidationError("Invalid action. Use 'add' or 'remove'.")

    # Check movie existence
    movie = utils.get_movie(update.movie_id)
    if not movie:
        raise movie_not_found(update.movie_id)

    # Determine target
    target_id = current_user.user_id
    if user_id:
        if current_user.role != "administrator":
            raise ForbiddenError("Not authorized to modify other users' lists.")
        target_id = user_id
        
    utils.update_watch_later(target_id, update.movie_id, update.action)
    return {"message": f"Movie {update.action}ed successfully."}


@router.get("/{movie_id}", response_model=schemas.Movie)
def get_movie(movie_id: str, current_user: UserToken = Depends(get_current_user)):
    movie = utils.get_movie(movie_id)
    if not movie:
        raise movie_not_found(movie_id)
    return movie
