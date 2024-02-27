from abc import ABC, abstractmethod
from typing import Any, Generic, Literal, Sequence, TypeVar

from systema.server.project_manager.models.item import (
    Item,
    ItemCreate,
    ItemRead,
    ItemUpdate,
)
from systema.server.project_manager.models.project import (
    Project,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)

T = TypeVar("T")


class Proxy(ABC, Generic[T]):
    @abstractmethod
    def all(self) -> Sequence[T]:
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
        return [ProjectRead.model_validate(p) for p in Project.list()]

    def create(self, data: ProjectCreate):
        return ProjectRead.model_validate(Project.create(data))

    def update(self, id: str, data: ProjectUpdate):
        return ProjectRead.model_validate(Project.update(id, data))

    def delete(self, id: str):
        Project.delete(id)


class ItemProxy(Proxy[ItemRead]):
    def __init__(self, project_id: str):
        self.project_id = project_id

    def all(self):
        return [ItemRead.from_task(*result) for result in Item.list(self.project_id)]

    def create(self, data: ItemCreate):
        return ItemRead.from_task(*Item.create(data, self.project_id))

    def update(self, id: str, data: ItemUpdate):
        return ItemRead.from_task(*Item.update(self.project_id, id, data))

    def delete(self, id: str):
        Item.delete(self.project_id, id)

    def move(self, id: str, up_or_down: Literal["up"] | Literal["down"]):
        return ItemRead.from_task(*Item.move(self.project_id, id, up_or_down))

    def toggle(self, id: str):
        return ItemRead.from_task(*Item.check_or_uncheck(self.project_id, id))
