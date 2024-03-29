from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from systema.models.task import (
    Task,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from systema.server.auth.utils import get_current_active_user
from systema.server.db import engine

router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(project_id: str, task: TaskCreate):
    db_task, _ = Task.create(task, project_id)
    return db_task


@router.get("/", response_model=list[TaskRead])
async def list_tasks(project_id: str):
    with Session(engine) as session:
        statement = select(Task).where(Task.project_id == project_id)
        if tasks := session.exec(statement).all():
            return tasks
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tasks not found")


@router.get("/{id}", response_model=TaskRead)
async def get_task(project_id: str, id: str):
    with Session(engine) as session:
        statement = select(Task).where(Task.project_id == project_id, Task.id == id)
        if task := session.exec(statement).first():
            return task
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")


@router.patch("/{id}", response_model=TaskRead)
async def edit_task(project_id: str, id: str, task: TaskUpdate):
    with Session(engine) as session:
        statement = select(Task).where(Task.project_id == project_id, Task.id == id)
        if db_task := session.exec(statement).first():
            db_task.sqlmodel_update(task.model_dump(exclude_unset=True))
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, id: str):
    with Session(engine) as session:
        statement = select(Task).where(Task.project_id == project_id, Task.id == id)
        if task := session.exec(statement).first():
            session.delete(task)
            session.commit()
            return
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
