"""Movie browsing and watch-later list routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
import tempfile, os, random, requests
from backend.authentication.security import get_current_user
from backend.authentication.schemas import UserToken
from backend.movies import utils, schemas
from backend.core.authz import require_role, block_if_penalized
from backend.core.jsonio import save_json
from dotenv import load_dotenv

router = APIRouter(prefix="/movies", tags=["Movies"])

load_dotenv()
API_TOKEN = os.getenv("TMDB_API_TOKEN")
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/popular"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}


@router.get("/", response_model=List[schemas.Movie])
def list_movies(params: schemas.MovieSearchParams = Depends()):
    """List, search, sort, and paginate movies."""
    movies = utils.load_movies()
    movies = utils.filter_movies(movies, params)
    movies = utils.sort_movies(movies, params.sort_by, params.order)
    return utils.paginate_movies(movies, params.page, params.limit)

@router.get("/random", summary="Get a random popular movie")
def get_random_popular_movie():
    """
    Fetches a random popular movie from TMDB.
    """
    # TMDB popular movies can have up to ~500 pages
    page = random.randint(1, 500)
    params = {"language": "en-US", "page": page}

    response = requests.get(TMDB_BASE_URL, headers=headers, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch data from TMDB")

    data = response.json()
    results = data.get("results", [])

    if not results:
        raise HTTPException(status_code=404, detail="No popular movies found")

    movie = random.choice(results)

    return {
        "id": movie.get("id"),
        "title": movie.get("title"),
        "overview": movie.get("overview"),
        "poster_path": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" 
                        if movie.get("poster_path") else None,
        "rating": movie.get("vote_average"),
        "release_date": movie.get("release_date")
    }

@router.get("/download")
def download_movies(background_tasks: BackgroundTasks, current_user: UserToken = Depends(get_current_user)):
    """Download all movies as a single JSON file (admin only)."""
    require_role(current_user, ["administrator"])
    movies = utils.load_movies()
    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    save_json(tmp_file.name, movies)
    background_tasks.add_task(os.remove, tmp_file.name)
    return FileResponse(tmp_file.name, filename="movies.json", media_type="application/json")


@router.get("/watch-later", response_model=schemas.WatchLaterResponse)
def get_watch_later(current_user: UserToken = Depends(get_current_user), user_id: Optional[str] = Query(None)):
    """View watch-later list (admin can specify another user ID)."""
    if user_id and current_user.role != "administrator":
        raise HTTPException(status_code=403, detail="Not authorized to view another user's list.")
    target_id = user_id or current_user.user_id
    movies = utils.get_watch_later(target_id)
    return {"user_id": target_id, "watch_later": movies}


@router.patch("/watch-later")
@block_if_penalized(["suspension"])
async def modify_watch_later(update: schemas.WatchLaterUpdate, current_user: UserToken = Depends(get_current_user), user_id: Optional[str] = Query(None)):
    """Add or remove movies from watch-later list. Admin may target another user."""
    if update.action not in ["add", "remove"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'add' or 'remove'.")

    if user_id and current_user.role != "administrator":
        raise HTTPException(status_code=403, detail="Not authorized to modify another user's list.")

    if not utils.get_movie(update.movie_id):
        raise HTTPException(status_code=404, detail="Movie not found.")

    target_id = user_id or current_user.user_id
    utils.update_watch_later(target_id, update.movie_id, update.action)
    return {"message": f"Movie {update.action}ed successfully."}


@router.get("/{movie_id}/book-time")
def get_movie_book_time(movie_id: str, current_user: UserToken = Depends(get_current_user)):
    """Estimate reading time if the movie were adapted as a book."""
    movie = utils.get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    duration = movie.get("duration")
    if duration is None:
        raise HTTPException(status_code=400, detail="Movie runtime is unavailable.")

    hours = (duration * 300) / 250 / 60
    message = f"If this movie were a book, it would take {hours:.2f} hours to read"
    return {"message": message}


@router.get("/{movie_id}", response_model=schemas.Movie)
def get_movie(movie_id: str, current_user: UserToken = Depends(get_current_user)):
    movie = utils.get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")
    return movie

