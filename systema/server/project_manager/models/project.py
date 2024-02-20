from datetime import datetime

from sqlmodel import Field, SQLModel

from systema.utils import BaseTableModel


class ProjectBase(SQLModel):
    name: str


class Project(ProjectBase, BaseTableModel, table=True):
    created_at: datetime = Field(default_factory=datetime.now, index=True)


class ProjectCreate(ProjectBase):
    ...


class ProjectRead(ProjectBase):
    id: str
    created_at: datetime


class ProjectUpdate(SQLModel):
    name: str | None = None
