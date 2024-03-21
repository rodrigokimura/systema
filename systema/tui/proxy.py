from abc import ABC, abstractmethod
from typing import Any, Generator, Generic, Literal, TypeVar

from systema.models.bin import Bin, BinCreate, BinRead, BinUpdate
from systema.models.card import Card, CardCreate, CardRead, CardUpdate
from systema.models.item import (
    Item,
    ItemCreate,
    ItemRead,
    ItemUpdate,
)
from systema.models.project import (
    Project,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)

T = TypeVar("T")


class Proxy(ABC, Generic[T]):
    @abstractmethod
    def all(self) -> Generator[T, None, None]:
        pass

    @abstractmethod
    def create(self, data: Any) -> T:
        pass

    @abstractmethod
    def update(self, id: str, data: Any) -> T:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass


class ProjectProxy(Proxy[ProjectRead]):
    def all(self):
        return Project.list()

    def create(self, data: ProjectCreate):
        return Project.create(data)

    def update(self, id: str, data: ProjectUpdate):
        return Project.update(id, data)

    def delete(self, id: str):
        Project.delete(id)


class ItemProxy(Proxy[ItemRead]):
    def __init__(self, project_id: str):
        self.project_id = project_id

    def all(self):
        return Item.list(self.project_id)

    def create(self, data: ItemCreate):
        return Item.create(data, self.project_id)

    def update(self, id: str, data: ItemUpdate):
        return Item.update(self.project_id, id, data)

    def delete(self, id: str):
        Item.delete(self.project_id, id)

    def move(self, id: str, up_or_down: Literal["up"] | Literal["down"]):
        return Item.move(self.project_id, id, up_or_down)

    def toggle(self, id: str):
        return Item.check_or_uncheck(self.project_id, id)


class BinProxy(Proxy[BinRead]):
    def __init__(self, board_id: str):
        self.board_id = board_id

    def all(self):
        return Bin.list(self.board_id)

    def create(self, data: BinCreate):
        return Bin.create(data, self.board_id)

    def update(self, id: str, data: BinUpdate):
        return Bin.update(self.board_id, id, data)

    def delete(self, id: str):
        Bin.delete(self.board_id, id)

    def move(self, id: str, direction: Literal["left"] | Literal["right"]):
        return Bin.move(self.board_id, id, direction)


class CardProxy(Proxy[CardRead]):
    def __init__(self, board_id: str):
        self.board_id = board_id

    def all(self):
        return Card.list(self.board_id)

    def create(self, data: CardCreate):
        return Card.create(data, self.board_id)

    def update(self, id: str, data: CardUpdate):
        return Card.update(self.board_id, id, data)

    def delete(self, id: str):
        Card.delete(self.board_id, id)

    def move(
        self,
        id: str,
        direction: Literal["up"] | Literal["down"] | Literal["left"] | Literal["right"],
    ):
        return Card.move(self.board_id, id, direction)
