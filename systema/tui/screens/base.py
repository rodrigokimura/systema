from abc import ABC, abstractmethod
from typing import TypeVar

from textual.app import ScreenStackError
from textual.reactive import var
from textual.screen import Screen

from systema.server.project_manager.models.project import ProjectRead
from systema.tui.proxy import Proxy


class BaseProjectScreen(ABC):
    @abstractmethod
    def get_proxy_type(self) -> type[Proxy[ProjectRead]]:
        pass


_Proxy = TypeVar("_Proxy", bound=Proxy)


class ProjectScreen(Screen[None]):
    project: var[ProjectRead | None] = var(None)

    def __init__(
        self,
        proxy_type: type[_Proxy],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.proxy_type = proxy_type

    async def watch_project(self, project: ProjectRead | None):
        if project:
            self.proxy = self.proxy_type(project.id)
            await self.clear()
            await self.populate()

    @abstractmethod
    async def populate(self):
        raise NotImplementedError

    @abstractmethod
    async def clear(self):
        raise NotImplementedError

    async def on_mount(self):
        await self.clear()
        await self.populate()

    def dismiss(self, result=None):
        print(f"Ignoring result={result}")

        try:
            return super().dismiss(None)
        except ScreenStackError:
            self.app.switch_mode("main")
