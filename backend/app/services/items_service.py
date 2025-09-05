import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from app.schemas.item import Item, ItemCreate
from app.repositories.items_repo import load_all, save_all

def list_items() -> List[Item]:
    return [Item(**it) for it in load_all()]

def create_item(payload: ItemCreate) -> Item:
    items = load_all()
    new_id = str(uuid.uuid4())
    if any(it.get("id") == new_id for it in items):  # extremely unlikely, but consistent check
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    new_item = Item(id=new_id, title=payload.title.strip(), category=payload.category.strip(), tags=payload.tags)
    items.append(new_item.dict())
    save_all(items)
    return new_item
