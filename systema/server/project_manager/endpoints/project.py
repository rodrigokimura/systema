from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from systema.server.auth.utils import get_current_active_user
from systema.server.db import engine
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
    with Session(engine) as session:
        db_project = Project.model_validate(project)
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
        return db_project


@router.get("/", response_model=list[ProjectRead])
async def list_projects():
    with Session(engine) as session:
        statement = select(Project)
        if projects := session.exec(statement).all():
            return projects
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Projects not found")


@router.get("/{id}", response_model=ProjectRead)
async def get_project(id: str):
    with Session(engine) as session:
        if project := session.get(Project, id):
            return project
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")


@router.patch("/{id}", response_model=ProjectRead)
async def edit_project(id: str, project: ProjectUpdate):
    with Session(engine) as session:
        if db_project := session.get(Project, id):
            db_project.sqlmodel_update(project.model_dump(exclude_unset=True))
            session.add(db_project)
            session.commit()
            session.refresh(db_project)
            return db_project
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(id: str):
    with Session(engine) as session:
        if project := session.get(Project, id):
            session.delete(project)
            session.commit()
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
