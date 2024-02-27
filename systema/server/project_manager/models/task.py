from __future__ import annotations

import enum
from datetime import datetime

from sqlmodel import Field, Session, select

from systema.base import BaseModel, IdMixin
from systema.server.db import engine
from systema.server.project_manager.models.project import Project


class Status(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskBase(BaseModel):
    name: str
    status: Status = Status.NOT_STARTED


class Task(TaskBase, IdMixin, table=True):
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    project_id: str = Field(..., foreign_key="project.id")

    @classmethod
    def get(cls, project_id: str, id: str):
        with Session(engine) as session:
            project = session.get(Project, project_id)
            if project is None:
                raise Project.NotFound()

            statement = select(Task).where(Task.project_id == project.id, Task.id == id)
            if item := session.exec(statement).first():
                return item

        raise Task.NotFound()

    @classmethod
    def create(cls, data: TaskCreate, project_id: str):
        with Session(engine) as session:
            if (project := session.get(Project, project_id)) and project.id:
                db_task = Task(name=data.name, project_id=project.id)
                session.add(db_task)
                session.commit()
                session.refresh(db_task)
                return db_task
            raise Project.NotFound()


class TaskCreate(TaskBase):
    ...


class TaskRead(TaskBase):
    id: str
    created_at: datetime
    status: Status

    def is_done(self):
        return self.status == Status.DONE


class TaskUpdate(BaseModel):
    name: str | None = None
    status: Status | None = None
