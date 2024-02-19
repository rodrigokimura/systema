from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from systema.server.project_manager.models.project import Project

from ...db import engine
from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


@router.post("/", response_model=TaskRead, status_code=HTTPStatus.CREATED)
async def create_task(project_id: UUID, task: TaskCreate):
    with Session(engine) as session:
        if (project := session.get(Project, project_id)) and project.id:
            db_task = Task(name=task.name, project_id=project.id)
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task
        raise HTTPException(HTTPStatus.NOT_FOUND, "Task not found")


@router.get("/", response_model=list[TaskRead])
async def list_tasks(project_id: UUID):
    with Session(engine) as session:
        statement = select(Task).where(Task.project_id == project_id)
        if tasks := session.exec(statement).all():
            return tasks
        raise HTTPException(HTTPStatus.NOT_FOUND, "Tasks not found")


@router.get("/{id}", response_model=TaskRead)
async def get_task(project_id: UUID, id: UUID):
    with Session(engine) as session:
        statement = select(Task).where(Task.project_id == project_id, Task.id == id)
        if task := session.exec(statement).first():
            return task
        raise HTTPException(404, "Task not found")


@router.patch("/{id}", response_model=TaskRead)
async def edit_task(project_id: UUID, id: UUID, task: TaskUpdate):
    with Session(engine) as session:
        statement = select(Task).where(Task.project_id == project_id, Task.id == id)
        if db_task := session.exec(statement).first():
            db_task.sqlmodel_update(task.model_dump(exclude_unset=True))
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task
        raise HTTPException(HTTPStatus.NOT_FOUND, "Task not found")


@router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_project(project_id: UUID, id: UUID):
    with Session(engine) as session:
        statement = select(Task).where(Task.project_id == project_id, Task.id == id)
        if task := session.exec(statement).first():
            session.delete(task)
            session.commit()
            return
        raise HTTPException(HTTPStatus.NOT_FOUND, "Task not found")