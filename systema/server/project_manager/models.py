from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ProjectBase(SQLModel):
    name: str
    created_at: datetime = Field(default_factory=datetime.now, index=True)


class Project(ProjectBase, table=True):
    id: UUID | None = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )


class ProjectCreate(ProjectBase):
    ...


class ProjectRead(ProjectBase):
    id: UUID
    created_at: datetime


class ProjectUpdate(SQLModel):
    name: str | None = None
