from fastapi import APIRouter
from typing import List
from app.schemas.item import Item, ItemCreate
from app.services.items_service import list_items, create_item

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=List[Item])
def get_items():
    return list_items()

@router.post("", response_model=Item, status_code=201)
def post_item(payload: ItemCreate):
    return create_item(payload)
