from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.authentication import router as authentication_router

app = FastAPI()

# Routers
app.include_router(authentication_router.router)

# Cors
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