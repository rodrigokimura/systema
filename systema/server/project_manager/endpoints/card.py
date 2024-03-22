from fastapi import APIRouter, Depends, status

from systema.models.card import Card, CardCreate, CardRead, CardUpdate
from systema.server.auth.utils import get_current_active_user

router = APIRouter(
    prefix="/projects/{project_id}/cards",
    tags=["cards"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=CardRead, status_code=status.HTTP_201_CREATED)
async def create_card(card: CardCreate, project_id: str):
    return Card.create(card, project_id)


@router.get("/", response_model=list[CardRead])
async def list_cards(project_id: str):
    return Card.list(project_id)


@router.get("/{id}", response_model=CardRead)
async def get_card(project_id: str, id: str):
    return Card.get(project_id, id)


@router.patch("/{id}", response_model=CardRead)
async def update_card(project_id: str, id: str, data: CardUpdate):
    return Card.update(project_id, id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(project_id: str, id: str):
    Card.delete(project_id, id)
