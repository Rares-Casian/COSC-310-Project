from fastapi import FastAPI
from routers.items import router as items_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("")
def get_item(name : str):
    return {"item ": name, "status": "ok"}

app.include_router(items_router)
