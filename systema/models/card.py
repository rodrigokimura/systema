from __future__ import annotations

from typing import Literal

from sqlmodel import Field, Session, col, select

from systema.base import BaseModel
from systema.models.task import Task, TaskCreate, TaskMixin, TaskRead, TaskUpdate
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


class Card(CardBase, TaskMixin[CardRead], table=True):
    id: str = Field(..., foreign_key="task.id", primary_key=True)

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
                    .where(Card.id == Task.id, Task.project_id == project_id)
                    .order_by(col(Card.order).desc())
                )
                max_card = session.exec(statement).first()
                max_order = max_card.order if max_card else 0
                if card.order == max_order:
                    return CardRead.from_task(card, task)

                card.order += 1
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
