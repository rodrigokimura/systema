import enum
from datetime import datetime

from sqlmodel import Field

from systema.base import BaseModel, IdMixin


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


class TaskCreate(TaskBase):
    ...


class TaskRead(TaskBase):
    id: str
    created_at: datetime
    status: Status


class TaskUpdate(BaseModel):
    name: str | None = None
    status: Status | None = None
