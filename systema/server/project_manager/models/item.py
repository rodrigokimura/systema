from __future__ import annotations

from typing import Literal

from sqlmodel import Field, Session, col, select

from systema.base import BaseModel
from systema.server.db import engine
from systema.server.project_manager.models.project import Project
from systema.server.project_manager.models.task import (
    Status,
    Task,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)


class ItemBase(BaseModel):
    order: int = Field(0, ge=0)


class Item(ItemBase, table=True):
    id: str = Field(..., foreign_key="task.id", primary_key=True)
    order: int = Field(0, ge=0)

    def _mode_down(self):
        self.order -= 1

    @classmethod
    def _get_project(cls, session: Session, project_id: str):
        if project := session.get(Project, project_id):
            return project
        raise Project.NotFound()

    @classmethod
    def _get_item_task(cls, session: Session, project: Project, id: str):
        statement = (
            select(Item, Task)
            .join(Task)
            .where(Task.project_id == project.id, Task.id == id)
        )
        if result := session.exec(statement).first():
            return result
        raise Item.NotFound()

    @classmethod
    def get(cls, project_id: str, id: str):
        with Session(engine) as session:
            project = cls._get_project(session, project_id)
            return cls._get_item_task(session, project, id)

    @classmethod
    def create(cls, data: ItemCreate, project_id: str):
        with Session(engine) as session:
            project = cls._get_project(session, project_id)

            task = Task.create(TaskCreate.model_validate(data), project_id)

            item = Item.model_validate(data, update={"id": task.id})
            session.add(item)
            session.commit()
            session.refresh(item)

            cls._reorder(session, project.id, item.order, exclude=item.id, shift=True)

            session.refresh(item)
            return item, task

    @classmethod
    def move(
        cls, project_id: str, id: str, up_or_down: Literal["up"] | Literal["down"]
    ):
        with Session(engine) as session:
            project = cls._get_project(session, project_id)
            item, task = cls._get_item_task(session, project, id)

            original_order = item.order

            if up_or_down == "up":
                item.order = max(0, item.order - 1)
            elif up_or_down == "down":
                statement = select(Item).order_by(col(Item.order).desc())
                max_item = session.exec(statement).first()
                max_order = max_item.order if max_item else 0
                if item.order == max_order:
                    return item, task

                item.order += 1
            else:
                raise ValueError()

            session.add(item)
            session.commit()
            session.refresh(item)

            cls._reorder(
                session,
                project.id,
                original_order,
                exclude=item.id,
                shift=False,
            )
            cls._reorder(
                session,
                project.id,
                item.order,
                exclude=item.id,
                shift=True,
            )

            session.add(item)
            session.commit()
            session.refresh(item)
            session.refresh(task)
            return item, task

    @classmethod
    def check_or_uncheck(cls, project_id: str, id: str):
        with Session(engine) as session:
            project = cls._get_project(session, project_id)
            item, task = cls._get_item_task(session, project, id)

            if task.status == Status.DONE:
                task.status = Status.NOT_STARTED
                original_order = 0
            else:
                task.status = Status.DONE
                original_order = item.order
                item.order = 0

            session.add_all((task, item))
            session.commit()

            session.refresh(item)
            session.refresh(task)

            cls._reorder(
                session, project_id, original_order, item.id, original_order == 0
            )

            session.refresh(item)
            session.refresh(task)

            return item, task

    @classmethod
    def update(cls, project_id: str, id: str, data: ItemUpdate):
        with Session(engine) as session:
            project = cls._get_project(session, project_id)
            item, task = cls._get_item_task(session, project, id)

            original_order = item.order

            task.sqlmodel_update(data.model_dump(exclude_unset=True))
            item.sqlmodel_update(data.model_dump(exclude_unset=True))

            session.add_all((item, task))
            session.commit()

            session.refresh(item)
            session.refresh(task)

            if original_order != item.order:
                cls._reorder(
                    session,
                    project.id,
                    original_order,
                    exclude=item.id,
                    shift=False,
                )
                cls._reorder(
                    session,
                    project.id,
                    item.order,
                    exclude=item.id,
                    shift=True,
                )

            session.refresh(item)
            session.refresh(task)

            return item, task

    @classmethod
    def delete(cls, project_id: str, id: str):
        with Session(engine) as session:
            project = cls._get_project(session, project_id)
            item, task = cls._get_item_task(session, project, id)

            cls._reorder(session, project_id, item.order, item.id, shift=False)

            session.delete(item)
            session.delete(task)

            session.commit()

    @classmethod
    def list(cls, project_id: str):
        with Session(engine) as session:
            project = cls._get_project(session, project_id)
            statement = (
                select(Item, Task)
                .join(Task)
                .join(Project)
                .where(
                    Item.id == Task.id,
                    Task.project_id == Project.id,
                    Project.id == project.id,
                )
                .order_by(
                    col(Item.order).asc(),
                    col(Task.status).asc(),
                )
            )
            return session.exec(statement).all()

    @classmethod
    def _reorder(
        cls,
        session: Session,
        project_id: str,
        order: int,
        exclude: str,
        shift: bool = True,
    ):
        statement = (
            select(Item)
            .join(Task)
            .where(
                Task.id == Item.id,
                Task.project_id == project_id,
                Item.order >= order,
                Task.status != Status.DONE,
                Item.id != exclude,
            )
            .order_by(col(Item.order).asc())
        )
        items = session.exec(statement).all()
        for i, item in enumerate(items):
            item.order = order + i
            if shift:
                item.order += 1
            session.add(item)
        session.commit()


class ItemCreate(ItemBase, TaskCreate):
    ...


class ItemRead(Item, TaskRead):
    @classmethod
    def from_task(cls, item: Item, task: Task):
        return ItemRead.model_validate(item, update=task.model_dump())


class ItemUpdate(ItemBase, TaskUpdate):
    ...
