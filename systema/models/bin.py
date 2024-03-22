from datetime import datetime
from typing import Literal

from sqlmodel import Field, Session, col, select

from systema.base import BaseModel, IdMixin
from systema.server.db import engine


class BinBase(BaseModel):
    name: str
    order: int = Field(0, ge=0)


class BinCreate(BinBase):
    pass


class BinUpdate(BaseModel):
    name: str | None = None
    order: int | None = None


class Bin(BinBase, IdMixin, table=True):
    board_id: str = Field(..., foreign_key="board.id")
    created_at: datetime = Field(default_factory=datetime.now, index=True)

    @classmethod
    def _get(cls, session: Session, board_id: str, id: str):
        statement = select(Bin).where(Bin.id == id, Bin.board_id == board_id)
        if result := session.exec(statement).first():
            return result
        raise Bin.NotFound()

    @classmethod
    def _get_board(cls, session: Session, board_id: str):
        from systema.models.board import Board

        if board := session.get(Board, board_id):
            return board
        raise Board.NotFound

    @classmethod
    def get(cls, board_id: str, id: str):
        with Session(engine) as session:
            return BinRead.from_bin(cls._get(session, board_id, id))

    @classmethod
    def create(cls, data: BinCreate, board_id: str):
        with Session(engine) as session:
            project = cls._get_board(session, board_id)
            bin = Bin(name=data.name, board_id=project.id, order=data.order)
            session.add(bin)
            session.commit()
            session.refresh(bin)
            cls._reorder(session, bin.board_id, bin.order, exclude=bin.id, shift=True)
            session.refresh(bin)
            return BinRead.from_bin(bin)

    @classmethod
    def move(
        cls, project_id: str, id: str, direction: Literal["right"] | Literal["left"]
    ):
        with Session(engine) as session:
            project = cls._get_board(session, project_id)
            bin = cls._get(session, project_id, id)

            original_order = bin.order

            if direction == "left":
                bin.order = max(0, bin.order - 1)
            elif direction == "right":
                statement = (
                    select(Bin)
                    .where(Bin.board_id == project_id)
                    .order_by(col(Bin.order).desc())
                )
                max_bin = session.exec(statement).first()
                max_order = max_bin.order if max_bin else 0
                if bin.order >= max_order:
                    return bin

                bin.order += 1
            else:
                raise ValueError()

            session.add(bin)
            session.commit()
            session.refresh(bin)

            cls._reorder(
                session,
                project.id,
                original_order,
                exclude=bin.id,
                shift=False,
            )
            cls._reorder(
                session,
                project.id,
                bin.order,
                exclude=bin.id,
                shift=True,
            )

            session.add(bin)
            session.commit()
            session.refresh(bin)
            return bin

    @classmethod
    def update(cls, board_id: str, id: str, data: BinUpdate):
        with Session(engine) as session:
            board = cls._get_board(session, board_id)
            bin = cls._get(session, board_id, id)

            original_order = bin.order

            bin.sqlmodel_update(data.model_dump(exclude_unset=True))

            session.add(bin)
            session.commit()

            session.refresh(bin)

            if original_order != bin.order:
                cls._reorder(
                    session,
                    board.id,
                    original_order,
                    exclude=bin.id,
                    shift=False,
                )
                cls._reorder(
                    session,
                    board.id,
                    bin.order,
                    exclude=bin.id,
                    shift=True,
                )

            session.refresh(bin)

            return BinRead.from_bin(bin)

    @classmethod
    def delete(cls, board_id: str, id: str):
        with Session(engine) as session:
            board = cls._get_board(session, board_id)
            bin = cls._get(session, board.id, id)

            cls._reorder(session, board_id, bin.order, bin.id, shift=False)

            session.delete(bin)

            session.commit()

    @classmethod
    def list(cls, board_id: str):
        with Session(engine) as session:
            board = cls._get_board(session, board_id)
            statement = (
                select(Bin)
                .where(
                    Bin.board_id == board.id,
                )
                .order_by(
                    col(Bin.order).asc(),
                )
            )
            return (BinRead.from_bin(row) for row in session.exec(statement).all())

    @classmethod
    def _reorder(
        cls,
        session: Session,
        board_id: str,
        order: int,
        exclude: str,
        shift: bool = True,
    ):
        statement = (
            select(Bin)
            .where(
                Bin.board_id == board_id,
                Bin.order >= order,
                Bin.id != exclude,
            )
            .order_by(col(Bin.order).asc())
        )
        bins = session.exec(statement).all()
        for i, bin in enumerate(bins):
            bin.order = order + i
            if shift:
                bin.order += 1
            session.add(bin)
        session.commit()


class BinRead(BinBase):
    id: str
    board_id: str
    created_at: datetime

    @classmethod
    def from_bin(cls, bin: Bin):
        return BinRead.model_validate(bin)
