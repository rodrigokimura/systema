from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, Session, select

from systema.base import BaseModel, IdMixin
from systema.server.db import engine
from systema.server.project_manager.models.list import List


def get_session():
    with Session(engine) as session:
        yield session


class ProjectBase(BaseModel):
    name: str


class Project(ProjectBase, IdMixin, table=True):
    created_at: datetime = Field(default_factory=datetime.now, index=True)

    @classmethod
    def list(cls):
        with Session(engine) as session:
            statement = select(cls)
            return session.exec(statement).all()

    @classmethod
    def get(cls, id: str):
        with Session(engine) as session:
            if project := session.get(cls, id):
                return project

            raise cls.NotFound()

    @classmethod
    def create(cls, data: ProjectCreate):
        project = Project.model_validate(data)
        with Session(engine) as session:
            session.add(project)
            session.commit()
            session.refresh(project)

            list_ = List(id=project.id)
            session.add(list_)
            session.commit()

            session.refresh(project)
            return project

    @classmethod
    def update(cls, id: str, data: ProjectUpdate):
        with Session(engine) as session:
            if db_project := session.get(Project, id):
                db_project.sqlmodel_update(data.model_dump(exclude_unset=True))
                session.add(db_project)
                session.commit()

                session.refresh(db_project)
                return db_project

            raise cls.NotFound()

    @classmethod
    def delete(cls, id: str):
        with Session(engine) as session:
            if project := session.get(Project, id):
                session.delete(project)
                session.commit()
                if list := session.get(List, id):
                    session.delete(list)
                    session.commit()
                return

            raise cls.NotFound()


class ProjectCreate(ProjectBase):
    ...


class ProjectRead(ProjectBase):
    id: str
    created_at: datetime


class ProjectUpdate(BaseModel):
    name: str | None = None
