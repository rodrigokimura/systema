from __future__ import annotations

from datetime import datetime

import textual.widgets
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive, var
from textual.widgets import Checkbox, Label, Static
from textual.widgets import ListView as _ListView
from textual.widgets import Select as _Select

from systema.server.project_manager.models.item import ItemRead
from systema.server.project_manager.models.project import ProjectRead


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
    dt: reactive[datetime] = reactive(datetime.now, layout=True)

    def watch_dt(self, dt: datetime):
        self.update(dt.strftime("%d/%m/%Y %H:%M:%S"))


class ListView(_ListView):
    BINDINGS = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
    ]

    class Focus(Message):
        list_view: ListView

    class Blur(Message):
        list_view: ListView

    def watch_has_focus(self, value: bool) -> None:
        if value is True:
            message = self.Focus()
            message.list_view = self
            self.post_message(message)
        else:
            message = self.Blur()
            message.list_view = self
            self.post_message(message)
        super().watch_has_focus(value)


class ProjectItem(Static):
    DEFAULT_CSS = """
        ProjectItem {
            layout: horizontal;
            align: center middle;
        }
        ProjectItem Label {
            margin: 1;
        }
        ProjectItem Timestamp {
            color: $text-muted;
            margin: 1;
        }
    """

    project: reactive[ProjectRead | None] = reactive(None)
    label: var[Label] = var(Label())
    timestamp: var[Timestamp] = var(Timestamp())

    def compose(self) -> ComposeResult:
        yield Label(classes="name")
        yield Timestamp(classes="created_at")

    async def watch_project(self, project: ProjectRead | None):
        if project is None:
            return
        async with self.batch():
            self.label.remove()
            self.timestamp.remove()

            self.label = Label(project.name)
            self.timestamp = Timestamp()
            self.timestamp.dt = project.created_at

            self.mount_all((self.label, self.timestamp))


class Item(Static):
    DEFAULT_CSS = """
        Item {
            layout: horizontal;
            align: left middle;
        }
        Item Label {
            margin: 1;
        }
        Item Timestamp {
            color: $text-muted;
            margin: 1;
        }
    """
    item: reactive[ItemRead | None] = reactive(None)
    checkbox: var[Checkbox] = var(Checkbox())
    timestamp: var[Timestamp] = var(Timestamp())

    class Changed(Message):
        item: ItemRead

    def compose(self) -> ComposeResult:
        yield self.checkbox
        yield self.timestamp

    async def watch_item(self, item: ItemRead | None):
        if item is None:
            return

        async with self.batch():
            self.checkbox.remove()
            self.checkbox = Checkbox(item.name, value=item.is_done())

            self.timestamp.remove()
            self.timestamp = Timestamp()
            self.timestamp.dt = item.created_at

            self.mount_all((self.checkbox, self.timestamp))

    @on(Checkbox.Changed)
    async def handle_checkbox_changed(self, message: Checkbox.Changed):
        message.stop()
        if self.item:
            new_message = self.Changed()
            new_message.item = self.item
            self.post_message(new_message)
