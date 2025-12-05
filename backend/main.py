from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from backend.authentication import router as authentication_router
from backend.movies import router as movies_router
from backend.reviews import router as reviews_router
from backend.reports import router as reports_router
from backend.penalties import router as penalties_router
from backend.users import router as users_router
from backend.dashboards import router as dashboard_router
from backend.friendship import router as friendship_router
from backend.recommendations import router as recommendations_router
from backend.core import exceptions
from pathlib import Path
import json
from External_API.TMDb_api import getTrending, save_tmdb_json

logger = logging.getLogger(__name__)


tags_metadata = [
    {
        "name": "Dashboard",
        "description": "Role-specific dashboards for authenticated users.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

# Include routers
app.include_router(authentication_router.router)
app.include_router(movies_router.router)
app.include_router(reviews_router.router)
app.include_router(reports_router.router)
app.include_router(penalties_router.router)
app.include_router(users_router.router)
app.include_router(dashboard_router.router)
app.include_router(friendship_router.router)
app.include_router(recommendations_router.router)


# Exception handlers
@app.exception_handler(exceptions.BaseAPIException)
async def custom_exception_handler(request: Request, exc: exceptions.BaseAPIException):
    """Handle custom API exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail
            }
        },
        headers=exc.headers
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors with consistent format."""
    errors = exc.errors()
    error_messages = [f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in errors]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": error_messages
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with logging."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def read_root():
    return {"message": "Backend is up"}

DATA_FILE = Path(__file__).parent / "data/tmdb_data.json"

@app.get("/trending")
async def get_trending_movies():
    save_tmdb_json(getTrending())
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        movies = data.get("results", [])
        if not isinstance(movies, list):
            movies = []
    except Exception as e:
        print("Failed to read JSON:", e)
        movies = []

    # Sort by vote_average descending
    movies_sorted = sorted(movies, key=lambda x: x.get("vote_average", 0), reverse=True)
    return movies_sorted
