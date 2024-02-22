from datetime import datetime
from typing import ClassVar

import textual.widgets
from rich.console import RenderableType
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Label, Static
from textual.widgets import ListView as _ListView
from textual.widgets import Select as _Select

from systema.server.project_manager.models.project import Project


class SelectOverlay(textual.widgets._select.SelectOverlay):
    BINDINGS = [
        Binding("k", "cursor_up", "Up", show=False),
        Binding("j", "cursor_down", "Down", show=False),
    ]


class Select(_Select):
    BINDINGS = [
        Binding("j, k", "show_overlay"),
        Binding("k", "show_overlay"),
    ]

    def compose(self) -> ComposeResult:
        yield textual.widgets._select.SelectCurrent(self.prompt)
        yield SelectOverlay()


class Timestamp(Label):
    def __init__(
        self,
        dt: datetime,
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        renderable = dt.strftime("%d/%m/%Y %H:%M:%S")
        super().__init__(
            renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )


class ListView(_ListView):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
    ]


class ProjectItem(Static):
    DEFAULT_CSS = """
        ProjectItem {
            layout: horizontal;
            align: center middle;
        }
        ProjectItem Label.name {
            margin: 1;
        }
        ProjectItem Timestamp.created_at {
            color: $text-muted;
            margin: 1;
        }
    """

    def __init__(
        self,
        project: Project,
        renderable: RenderableType = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.project = project
        super().__init__(
            renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def compose(self) -> ComposeResult:
        yield Label(self.project.name, classes="name")
        yield Timestamp(self.project.created_at, classes="created_at")
