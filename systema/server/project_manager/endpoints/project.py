from fastapi import APIRouter, Depends, HTTPException, status

from systema.server.auth.utils import get_current_active_user
from systema.server.project_manager.models.project import (
    Project,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    return Project.create(project)


@router.get("/", response_model=list[ProjectRead])
async def list_projects():
    return Project.list()


@router.get("/{id}", response_model=ProjectRead)
async def get_project(id: str):
    try:
        return Project.get(id)
    except Project.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")


@router.patch("/{id}", response_model=ProjectRead)
async def edit_project(id: str, project: ProjectUpdate):
    try:
        return Project.update(id, project)
    except Project.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(id: str):
    try:
        Project.delete(id)
    except Project.NotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
