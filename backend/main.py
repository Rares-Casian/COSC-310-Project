from dotenv import load_dotenv
load_dotenv()
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
from backend.core import exceptions

logger = logging.getLogger(__name__)



app = FastAPI()

# Include routers
app.include_router(authentication_router.router)
app.include_router(movies_router.router)
app.include_router(reviews_router.router)
app.include_router(reports_router.router)
app.include_router(penalties_router.router)
app.include_router(users_router.router)


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
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def read_root():
    return {"message": "Backend is up"}
