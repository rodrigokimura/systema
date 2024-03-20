from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalScroll
from textual.reactive import var
from textual.widgets import Footer, Header, Label

from systema.models.project import ProjectRead
from systema.tui.proxy import BinProxy, CardProxy
from systema.tui.screens.base import ProjectScreen
from systema.tui.widgets import Bin as BinWidget
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
    CSS_PATH = "styles/kanban.css"

    current_item: var[Item | None] = var(None)
    proxy: CardProxy
    bin_proxy: BinProxy

    async def watch_project(self, project: ProjectRead | None):
        if project:
            self.bin_proxy = BinProxy(project.id)
        await super().watch_project(project)

    def compose(self) -> ComposeResult:
        yield Header()
        self.cont = HorizontalScroll()
        yield self.cont
        yield Footer()

    async def clear(self):
        async with self.batch():
            for w in self.cont.query(Label):
                w.remove()

    async def populate(self):
        cards = list(self.proxy.all())
        print("asdfasdf")
        print(cards)
        bin = BinWidget()
        bin.border_title = "No bin"
        self.cont.mount(bin)

        for b in self.bin_proxy.all():
            bin = BinWidget()
            bin.border_title = b.name
            self.cont.mount(bin)
