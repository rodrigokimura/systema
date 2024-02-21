from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, Session, SQLModel

from systema.utils import BaseTableModel


class ProjectBase(SQLModel):
    name: str


class Project(ProjectBase, BaseTableModel, table=True):
    created_at: datetime = Field(default_factory=datetime.now, index=True)

    @staticmethod
    def create(data: ProjectCreate):
        from systema.server.db import engine

        project = Project(name=data.name)
        with Session(engine) as session:
            session.add(project)
            session.commit()
            session.refresh(project)
            return project

    @staticmethod
    def delete(id: str):
        from systema.server.db import engine

        with Session(engine) as session:
            if project := session.get(Project, id):
                session.delete(project)
                session.commit()


class ProjectCreate(ProjectBase):
    ...


class ProjectRead(ProjectBase):
    id: str
    created_at: datetime


class ProjectUpdate(SQLModel):
    name: str | None = None
