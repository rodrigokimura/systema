from uuid import UUID

from fastapi import APIRouter
from sqlmodel import Session, select

from ..db import engine
from .models import Project

router = APIRouter()


@router.post("/projects")
async def create_project(project: Project):
    with Session(engine) as session:
        session.add(project)
        session.commit()
        session.refresh(project)
        return project


@router.get("/projects")
async def list_projects():
    with Session(engine) as session:
        statement = select(Project)
        projects = session.exec(statement).all()
        return projects


@router.get("/projects/{id}")
async def get_project(id: UUID):
    with Session(engine) as session:
        statement = select(Project).where(Project.id == id)
        project = session.exec(statement).one()
        return project


@router.put("/projects/{id}")
async def replace_project(id: UUID, project: Project):
    with Session(engine) as session:
        statement = select(Project).where(Project.id == id)
        project = session.exec(statement).one()
        return project


@router.delete("/projects/{id}")
async def delete_project(id: UUID):
    with Session(engine) as session:
        statement = select(Project).where(Project.id == id)
        project = session.exec(statement).one()
        session.delete(project)
        session.commit()
