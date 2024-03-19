from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalScroll
from textual.reactive import var
from textual.widgets import Footer, Header, Label

from systema.tui.proxy import ItemProxy
from systema.tui.screens.base import ProjectScreen
from systema.tui.widgets import Item


class KanbanScreen(ProjectScreen):
    BINDINGS = [
        Binding("q,escape", "dismiss", "Quit"),
        # Binding("a", "add_item", "Add", show=True),
        # Binding("e", "edit_item", "Edit", show=True),
        # Binding("d", "delete_item", "Delete", show=True),
        # Binding("ctrl+down,ctrl+j", "move_down", "Move down", show=True),
        # Binding("ctrl+up,ctrl+k", "move_up", "Move up", show=True),
        # Binding("space,enter", "toggle_item", "Check/Uncheck", show=True),
        # Binding("t", "toggle_collapsible", "Show/Hide completed", show=True),
        Binding("m", "select_mode", "Select mode", show=True),
    ]
    CSS_PATH = "styles/list.css"

    current_item: var[Item | None] = var(None)
    proxy: ItemProxy

    def compose(self) -> ComposeResult:
        yield Header()
        with HorizontalScroll():
            yield Label("test")
        yield Footer()

    async def clear(self):
        pass

    async def populate(self):
        pass
