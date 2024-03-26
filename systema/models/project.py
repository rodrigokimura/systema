from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, Session, select

from systema.base import BaseModel, IdMixin
from systema.server.db import engine


class SubProjectMixin(BaseModel):
    id: str = Field(..., foreign_key="project.id", primary_key=True)


class ProjectBase(BaseModel):
    name: str


class Project(ProjectBase, IdMixin, table=True):
    created_at: datetime = Field(default_factory=datetime.now, index=True)

    @classmethod
    def list(cls):
        with Session(engine) as session:
            statement = select(cls)
            return (
                ProjectRead.model_validate(row) for row in session.exec(statement).all()
            )

    @classmethod
    def get(cls, id: str):
        with Session(engine) as session:
            if project := session.get(cls, id):
                return project

            raise cls.NotFound()

    @classmethod
    def create(cls, data: ProjectCreate):
        from systema.models.board import Board
        from systema.models.checklist import Checklist

        project = Project.model_validate(data)
        with Session(engine) as session:
            session.add(project)
            session.commit()
            session.refresh(project)

            list_ = Checklist(id=project.id)
            board = Board(id=project.id)

            session.add_all((list_, board))
            session.commit()

            session.refresh(board)
            board.create_default_bins(session)

            session.refresh(project)
            return ProjectRead.model_validate(project)

    @classmethod
    def update(cls, id: str, data: ProjectUpdate):
        with Session(engine) as session:
            if db_project := session.get(Project, id):
                db_project.sqlmodel_update(data.model_dump(exclude_unset=True))
                session.add(db_project)
                session.commit()

                session.refresh(db_project)
                return ProjectRead.model_validate(db_project)

            raise cls.NotFound()

    @classmethod
    def delete(cls, id: str):
        from systema.models.board import Board
        from systema.models.checklist import Checklist

        with Session(engine) as session:
            if project := session.get(Project, id):
                session.delete(project)
                if list_ := session.get(Checklist, id):
                    session.delete(list_)
                if board := session.get(Board, id):
                    session.delete(board)
                session.commit()
                return

            raise cls.NotFound()


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: str
    created_at: datetime


class ProjectUpdate(BaseModel):
    name: str | None = None
