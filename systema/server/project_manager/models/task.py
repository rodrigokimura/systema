from datetime import datetime

from sqlmodel import Field, SQLModel

from systema.utils import BaseTableModel


class TaskBase(SQLModel):
    name: str


class Task(TaskBase, BaseTableModel, table=True):
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    project_id: str = Field(..., foreign_key="project.id")


class TaskCreate(TaskBase):
    ...


class TaskRead(TaskBase):
    id: str
    created_at: datetime


class TaskUpdate(SQLModel):
    name: str | None = None
