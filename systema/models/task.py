from __future__ import annotations

import enum
from abc import abstractmethod
from datetime import datetime
from typing import Any, Generator, Generic, Self, TypeVar

from sqlmodel import Field, Session, col, select

from systema.base import BaseModel, IdMixin
from systema.models.project import Project
from systema.server.db import engine


class SubTaskMixin(BaseModel):
    id: str = Field(..., foreign_key="task.id", primary_key=True)


class TaskReadMixin(BaseModel):
    @classmethod
    def from_task(cls, obj: Any, task: Task):
        return cls.model_validate(obj, update=task.model_dump())


T = TypeVar("T", bound=TaskReadMixin)


class TaskMixin(BaseModel, Generic[T]):
    @staticmethod
    def get_project(session: Session, project_id: str):
        if project := session.get(Project, project_id):
            return project
        raise Project.NotFound()

    @classmethod
    def get_task(cls, session: Session, project: Project, id: str):
        statement = (
            select(cls, Task)
            .join(Task)
            .where(Task.project_id == project.id, Task.id == id)
        )
        if result := session.exec(statement).first():
            return result
        raise cls.NotFound()

    @classmethod
    def list(cls, project_id: str) -> Generator[T, None, None]:
        read_model = cls.get_read_model()
        with Session(engine) as session:
            project = cls.get_project(session, project_id)
            statement = (
                select(cls, Task)
                .join(Task)
                .join(Project)
                .where(
                    cls.id == Task.id,
                    Task.project_id == Project.id,
                    Project.id == project.id,
                )
                .order_by(
                    col(cls.order).asc(),
                    col(Task.status).asc(),
                )
            )
            return (read_model.from_task(*row) for row in session.exec(statement).all())

    @classmethod
    def get(cls, project_id: str, id: str):
        read_model = cls.get_read_model()
        with Session(engine) as session:
            project = cls.get_project(session, project_id)
            return read_model.from_task(*cls.get_task(session, project, id))

    @classmethod
    def create(cls, data: TaskCreate, project_id: str):
        read_model = cls.get_read_model()
        with Session(engine) as session:
            task, subclass_instances = Task.create(session, data, project_id)
            obj = next(i for i in subclass_instances if isinstance(i, cls))
            session.refresh(obj)
            return read_model.from_task(obj, task)

    @classmethod
    def update(cls, project_id: str, id: str, data: TaskUpdate):
        read_model = cls.get_read_model()
        with Session(engine) as session:
            project = cls.get_project(session, project_id)
            obj, task = cls.get_task(session, project, id)

            original_obj = obj.model_copy()

            task.sqlmodel_update(data.model_dump(exclude_unset=True))
            obj.sqlmodel_update(data.model_dump(exclude_unset=True))

            session.add_all((obj, task))
            session.commit()

            session.refresh(obj)
            session.refresh(task)

            cls.post_update(session, project, original_obj, obj)

            session.refresh(obj)
            session.refresh(task)

            return read_model.from_task(obj, task)

    @classmethod
    def delete(cls, project_id: str, id: str):
        with Session(engine) as session:
            project = cls.get_project(session, project_id)
            obj, task = cls.get_task(session, project, id)

            original_obj = obj.model_copy()

            if cls.pre_delete(session, project, original_obj):
                session.delete(obj)
                session.delete(task)

                session.commit()

    @classmethod
    def post_update(
        cls,
        session: Session,
        project: Project,
        original_obj: Self,
        current_obj: Self,
    ) -> Self:
        return current_obj

    @classmethod
    def pre_delete(
        cls,
        session: Session,
        project: Project,
        original_obj: Self,
    ) -> bool:
        return True

    @staticmethod
    @abstractmethod
    def get_read_model() -> type[T]:
        pass


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

    @staticmethod
    def get_project(session: Session, project_id: str):
        if project := session.get(Project, project_id):
            return project
        raise Project.NotFound()

    @classmethod
    def get(cls, project_id: str, id: str):
        with Session(engine) as session:
            project = cls.get_project(session, project_id)

            statement = select(Task).where(Task.project_id == project.id, Task.id == id)
            if item := session.exec(statement).first():
                return item

        raise Task.NotFound()

    @classmethod
    def create(cls, session: Session, data: TaskCreate, project_id: str):
        project = cls.get_project(session, project_id)
        db_task = Task(name=data.name, project_id=project.id)
        session.add(db_task)
        session.commit()

        subclass_instances = cls.create_subclass_instances(session, db_task)

        session.refresh(db_task)
        return db_task, subclass_instances

    @classmethod
    def create_subclass_instances(cls, session: Session, task: Task):
        from systema.models.card import Card
        from systema.models.item import Item

        item = Item._create(session, task)
        card = Card._create(session, task)
        return (item, card)


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase, TaskReadMixin):
    id: str
    created_at: datetime
    status: Status

    def is_done(self):
        return self.status == Status.DONE


class TaskUpdate(BaseModel):
    name: str | None = None
    status: Status | None = None
