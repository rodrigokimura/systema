from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from ..db import engine
from .models import Project, ProjectCreate, ProjectUpdate

router = APIRouter()


@router.post("/projects", response_model=Project, status_code=HTTPStatus.CREATED)
async def create_project(project: ProjectCreate):
    with Session(engine) as session:
        db_project = Project.model_validate(project)
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
        return db_project


@router.get("/projects", response_model=list[Project])
async def list_projects():
    with Session(engine) as session:
        statement = select(Project)
        projects = session.exec(statement).all()
        return projects


@router.get("/projects/{id}", response_model=Project)
async def get_project(id: UUID):
    with Session(engine) as session:
        db_project = session.get(Project, id)
        if not db_project:
            raise HTTPException(404, "Project not found")
        return db_project


@router.patch("/projects/{id}", response_model=Project)
async def edit_project(id: UUID, project: ProjectUpdate):
    with Session(engine) as session:
        db_project = session.get(Project, id)
        if not db_project:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Project not found")
        db_project.sqlmodel_update(project.model_dump(exclude_unset=True))
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
        return db_project


@router.delete("/projects/{id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_project(id: UUID):
    with Session(engine) as session:
        db_project = session.get(Project, id)
        if not db_project:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Project not found")
        session.delete(db_project)
        session.commit()
