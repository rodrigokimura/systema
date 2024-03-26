from __future__ import annotations

from typing import Literal

from sqlmodel import Field, Session, col, select

from systema.base import BaseModel
from systema.models.bin import Bin
from systema.models.project import Project
from systema.models.task import (
    SubTaskMixin,
    Task,
    TaskCreate,
    TaskMixin,
    TaskRead,
    TaskUpdate,
)
from systema.server.db import engine


class CardBase(BaseModel):
    order: int = Field(0, ge=0)
    bin_id: str | None = Field(None, foreign_key="bin.id", nullable=True)


class CardCreate(TaskCreate):
    pass


class CardRead(TaskRead, CardBase):
    pass


class CardUpdate(CardBase, TaskUpdate):
    pass


class Card(SubTaskMixin, CardBase, TaskMixin[CardRead], table=True):
    @staticmethod
    def get_read_model():
        return CardRead

    @classmethod
    def _create(cls, session: Session, task: Task):
        session.refresh(task)
        card = Card.model_validate(task)
        session.add(card)
        session.commit()
        session.refresh(card)

        cls._reorder(
            session,
            task.project_id,
            card.bin_id,
            card.order,
            exclude=card.id,
            shift=True,
        )

        session.refresh(card)
        return card

    @classmethod
    def _reorder(
        cls,
        session: Session,
        project_id: str,
        bin_id: str | None,
        order: int,
        exclude: str,
        shift: bool = True,
    ):
        statement = (
            select(cls)
            .join(Task)
            .where(
                Task.id == cls.id,
                Task.project_id == project_id,
                cls.bin_id == bin_id,
                cls.order >= order,
                cls.id != exclude,
            )
            .order_by(col(cls.order).asc())
        )
        cards = session.exec(statement).all()
        for i, item in enumerate(cards):
            item.order = order + i
            if shift:
                item.order += 1
            session.add(item)
        session.commit()

    @classmethod
    def move(
        cls,
        project_id: str,
        id: str,
        direction: Literal["up"] | Literal["down"] | Literal["left"] | Literal["right"],
    ):
        with Session(engine) as session:
            project = cls.get_project(session, project_id)
            card, task = cls.get_task(session, project, id)

            original_card = card.model_copy()

            if direction == "up":
                card.order = max(0, card.order - 1)
            elif direction == "down":
                statement = (
                    select(Card)
                    .join(Task)
                    .where(
                        Card.bin_id == card.bin_id,
                        Card.id == Task.id,
                        Task.project_id == project_id,
                    )
                    .order_by(col(Card.order).desc())
                )
                max_card = session.exec(statement).first()
                max_order = max_card.order if max_card else 0

                if card.order >= max_order:
                    return CardRead.from_task(card, task)

                card.order += 1
            elif direction in ("left", "right"):
                cls._move_x(session, card, project, direction)
            else:
                raise ValueError()

            session.add(card)
            session.commit()
            session.refresh(card)

            cls._reorder(
                session,
                project.id,
                original_card.bin_id,
                original_card.order,
                exclude=card.id,
                shift=False,
            )
            cls._reorder(
                session,
                project.id,
                card.bin_id,
                card.order,
                exclude=card.id,
                shift=True,
            )

            session.add(card)
            session.commit()
            session.refresh(card)
            session.refresh(task)
            return CardRead.from_task(card, task)

    @classmethod
    def _move_x(
        cls,
        session: Session,
        card: Card,
        project: Project,
        direction: Literal["left"] | Literal["right"],
    ):
        current_bin = session.exec(select(Bin).where(Bin.id == card.bin_id)).first()

        if direction == "left":
            target_order = (current_bin.order - 1) if current_bin else 0
        elif direction == "right":
            target_order = (current_bin.order + 1) if current_bin else 0
        else:
            raise ValueError

        if target_order == -1:
            card.bin_id = None
            card.order = 0
            return

        target_bin = session.exec(
            select(Bin).where(
                Bin.board_id == project.id,
                Bin.order == target_order,
            )
        ).first()

        if target_bin is None:
            return

        card.bin_id = target_bin.id
        card.order = 0

        cls._reorder(
            session,
            project.id,
            card.bin_id,
            card.order,
            exclude=card.id,
            shift=True,
        )
