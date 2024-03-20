from fastapi import APIRouter, Depends, status

from systema.models.bin import Bin, BinCreate, BinRead, BinUpdate
from systema.server.auth.utils import get_current_active_user

router = APIRouter(
    prefix="/projects/{project_id}/bins",
    tags=["bins"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=BinRead, status_code=status.HTTP_201_CREATED)
async def create_bin(bin: BinCreate, project_id: str):
    return Bin.create(bin, project_id)


@router.get("/", response_model=list[BinRead])
async def list_bins(project_id: str):
    return Bin.list(project_id)


@router.get("/{id}", response_model=BinRead)
async def get_bin(project_id: str, id: str):
    return Bin.get(project_id, id)


@router.patch("/{id}", response_model=BinRead)
async def update_bin(project_id: str, id: str, data: BinUpdate):
    return Bin.update(project_id, id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bin(project_id: str, id: str):
    Bin.delete(project_id, id)
