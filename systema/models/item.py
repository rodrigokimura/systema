from __future__ import annotations

from typing import Literal, Self

from sqlmodel import Field, Session, col, select

from systema.base import BaseModel
from systema.models.project import Project
from systema.models.task import (
    Status,
    SubTaskMixin,
    Task,
    TaskCreate,
    TaskMixin,
    TaskRead,
    TaskUpdate,
)
from systema.server.db import engine


class ItemBase(BaseModel):
    order: int = Field(0, ge=0)


class ItemCreate(TaskCreate):
    pass


class ItemRead(TaskRead, ItemBase):
    pass


class ItemUpdate(ItemBase, TaskUpdate):
    pass


class Item(SubTaskMixin, ItemBase, TaskMixin[ItemRead], table=True):
    @staticmethod
    def get_read_model():
        return ItemRead

    @classmethod
    def _create(cls, session: Session, task: Task):
        session.refresh(task)
        item = Item.model_validate(task)
        session.add(item)
        session.commit()
        session.refresh(item)

        cls._reorder(session, task.project_id, item.order, exclude=item.id, shift=True)

        session.refresh(item)
        return item

    @classmethod
    def move(
        cls, project_id: str, id: str, up_or_down: Literal["up"] | Literal["down"]
    ):
        with Session(engine) as session:
            project = cls.get_project(session, project_id)
            item, task = cls.get_task(session, project, id)

            original_order = item.order

            if up_or_down == "up":
                item.order = max(0, item.order - 1)
            elif up_or_down == "down":
                statement = select(Item).order_by(col(Item.order).desc())
                max_item = session.exec(statement).first()
                max_order = max_item.order if max_item else 0
                if item.order >= max_order:
                    return ItemRead.from_task(item, task)

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
            return ItemRead.from_task(item, task)

    @classmethod
    def check_or_uncheck(cls, project_id: str, id: str):
        with Session(engine) as session:
            project = cls.get_project(session, project_id)
            item, task = cls.get_task(session, project, id)

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

            return ItemRead.from_task(item, task)

    @classmethod
    def post_update(
        cls,
        session: Session,
        project: Project,
        original_obj: Self,
        current_obj: Self,
    ):
        original_order = original_obj.order

        if original_order != current_obj.order:
            cls._reorder(
                session,
                project.id,
                original_order,
                exclude=current_obj.id,
                shift=False,
            )
            cls._reorder(
                session,
                project.id,
                current_obj.order,
                exclude=current_obj.id,
                shift=True,
            )
        session.refresh(current_obj)
        return current_obj

    @classmethod
    def pre_delete(
        cls,
        session: Session,
        project: Project,
        original_obj: Self,
    ):
        cls._reorder(
            session, project.id, original_obj.order, original_obj.id, shift=False
        )
        return True

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
