from __future__ import annotations

from sqlmodel import Field, Session, select

from systema.base import BaseModel
from systema.server.db import engine
from systema.server.project_manager.models.project import Project
from systema.server.project_manager.models.task import (
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

    @classmethod
    def get(cls, project_id: str, id: str):
        with Session(engine) as session:
            if not (project := session.get(Project, project_id)):
                raise Project.NotFound()

            statement = (
                select(Item, Task)
                .join(Task)
                .where(Task.project_id == project.id, Task.id == id)
            )
            if result := session.exec(statement).first():
                return result

        raise Item.NotFound()

    @classmethod
    def create(cls, data: ItemCreate, project_id: str):
        with Session(engine) as session:
            if not (project := session.get(Project, project_id)):
                raise Project.NotFound()

            task = Task.create(TaskCreate.model_validate(data), project_id)

            item = Item.model_validate(data, update={"id": task.id})
            session.add(item)
            session.commit()
            session.refresh(item)

            cls._reorder(session, project.id, item.order, exclude=item.id, shift=True)

            session.refresh(item)
            return item, task

    @classmethod
    def update(cls, project_id: str, id: str, data: ItemUpdate):
        with Session(engine) as session:
            if not (project := session.get(Project, project_id)):
                raise Project.NotFound()

            statement = (
                select(Item, Task)
                .join(Task)
                .where(Task.project_id == project.id, Task.id == id)
            )
            if not (result := session.exec(statement).first()):
                raise Item.NotFound()
            item, task = result
            original_order = item.order

            task.sqlmodel_update(data.model_dump(exclude_unset=True))
            item.sqlmodel_update(data.model_dump(exclude_unset=True))

            session.add(item)
            session.add(task)
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
            if not (project := session.get(Project, project_id)):
                raise Project.NotFound()

            statement = (
                select(Item, Task)
                .join(Task)
                .where(Task.project_id == project.id, Task.id == id)
            )
            if not (result := session.exec(statement).first()):
                raise Item.NotFound()
            item, task = result

            cls._reorder(session, project_id, item.order, item.id, shift=False)

            session.delete(item)
            session.delete(task)

            session.commit()

    @classmethod
    def list(cls, project_id: str):
        with Session(engine) as session:
            statement = (
                select(Item, Task)
                .join(Task)
                .join(Project)
                .where(
                    Item.id == Task.id,
                    Task.project_id == Project.id,
                    Project.id == project_id,
                )
                .order_by("order")
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
                Item.id != exclude,
            )
            .order_by("order")
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
