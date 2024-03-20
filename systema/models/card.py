from __future__ import annotations

from sqlmodel import Field, Session, col, select

from systema.base import BaseModel
from systema.models.task import Task, TaskCreate, TaskMixin, TaskRead, TaskUpdate


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

        cls._reorder(session, task.project_id, card.order, exclude=card.id, shift=True)

        session.refresh(card)
        return card

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
            select(cls)
            .join(Task)
            .where(
                Task.id == cls.id,
                Task.project_id == project_id,
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
