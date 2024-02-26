from fastapi import APIRouter, Depends, status

from systema.server.auth.utils import get_current_active_user
from systema.server.project_manager.models.item import (
    Item,
    ItemCreate,
    ItemRead,
    ItemUpdate,
)

router = APIRouter(
    prefix="/projects/{project_id}/items",
    tags=["items"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, project_id: str):
    return ItemRead.from_task(*Item.create(item, project_id))


@router.get("/", response_model=list[ItemRead])
async def list_items(project_id: str):
    return (ItemRead.from_task(*result) for result in Item.list(project_id))


@router.get("/{id}", response_model=ItemRead)
async def get_item(project_id: str, id: str):
    return ItemRead.from_task(*Item.get(project_id, id))


@router.patch("/{id}", response_model=ItemRead)
async def update_item(project_id: str, id: str, data: ItemUpdate):
    return ItemRead.from_task(*Item.update(project_id, id, data))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(project_id: str, id: str):
    Item.delete(project_id, id)
