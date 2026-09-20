from fastapi import (FastAPI,HTTPException,Query,Response)
from pydantic import BaseModel, Field
from pathlib import Path
from fastapi.staticfiles import StaticFiles
app = FastAPI()
class ItemCreate(BaseModel):
    name: str
    price: float
class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
class ItemPublic(BaseModel):
    id: int
    name: str
    price: float
class ItemListResponse(BaseModel):
    items: list[ItemPublic]
    total: int
    skip: int
    limit: int
items = []
next_id = 1

@app.get("/items",response_model=ItemListResponse)
def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    min_price: float | None = None,
    max_price: float | None = None,
    q: str | None = Query(None, min_length=2),
    sort_by: str = Query("id", pattern="^(id|name|price)$"),
    order: str = Query("asc", pattern="^(asc|desc)$")
):
    result = items.copy()
    if min_price is not None:
        result = [
            item for item in result
            if item["price"] >= min_price
        ]
    if max_price is not None:
        result = [
            item for item in result
            if item["price"] <= max_price
        ]
    if q is not None:
        result = [
            item for item in result
            if q.lower() in item["name"].lower()
        ]
    result.sort(key=lambda item: item[sort_by],reverse=(order == "desc"))

    total = len(result)
    paginated_items = result[skip:skip + limit]
    return {"items": paginated_items,"total": total,"skip": skip,"limit": limit}

@app.get("/items/{item_id}",response_model=ItemPublic)
def get_item(item_id: int):
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404,detail="Item not found")

@app.post("/items",response_model=ItemPublic,status_code=201)
def create_item(item: ItemCreate):
    global next_id
    for existing_item in items:
        if existing_item["name"].lower() == item.name.lower():
            raise HTTPException(
                status_code=409,
                detail="Item with this name already exists"
            )
    new_item = {"id": next_id,"name": item.name,"price": item.price}
    items.append(new_item)
    next_id += 1
    return new_item

@app.put("/items/{item_id}",response_model=ItemPublic)
def update_item(item_id: int,item: ItemCreate):
    for index, existing_item in enumerate(items):
        if existing_item["id"] == item_id:
            if existing_item["name"].lower() != item.name.lower():
                for other_item in items:
                    if (
                        other_item["id"] != item_id
                        and other_item["name"].lower() == item.name.lower()
                    ):
                        raise HTTPException(status_code=409,detail="Item with this name already exists")
            updated_item = {"id": item_id,"name": item.name,"price": item.price}
            items[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404,detail="Item not found")

@app.patch("/items/{item_id}",response_model=ItemPublic)
def patch_item(item_id: int,item: ItemUpdate):
    for index, existing_item in enumerate(items):
        if existing_item["id"] == item_id:
            update_data = item.model_dump(
                exclude_unset=True
            )
            if (
                "name" in update_data
                and update_data["name"] is not None
                and update_data["name"].lower()
                != existing_item["name"].lower()
            ):
                for other_item in items:
                    if (
                        other_item["id"] != item_id
                        and other_item["name"].lower()
                        == update_data["name"].lower()
                    ):
                        raise HTTPException(status_code=409,detail="Item with this name already exists")
            items[index].update(update_data)
            return items[index]
    raise HTTPException(status_code=404,detail="Item not found")

@app.delete("/items/{item_id}",status_code=204)
def delete_item(item_id: int):
    for index, item in enumerate(items):
        if item["id"] == item_id:
            items.pop(index)
            return Response(
                status_code=204
            )
    raise HTTPException(status_code=404,detail="Item not found")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/",StaticFiles(directory=str(FRONTEND_DIR),html=True),name="frontend")