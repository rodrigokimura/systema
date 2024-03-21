from contextlib import asynccontextmanager
from typing import Literal

from textual.app import ComposeResult, events, on
from textual.binding import Binding
from textual.containers import HorizontalScroll
from textual.reactive import var
from textual.widgets import Footer, Header

from systema.models.project import ProjectRead
from systema.tui.proxy import BinProxy, CardProxy
from systema.tui.screens.base import ProjectScreen
from systema.tui.widgets import Bin as BinWidget
from systema.tui.widgets import Card as CardWidget


class KanbanScreen(ProjectScreen):
    BINDINGS = [
        Binding("q,escape", "dismiss", "Quit"),
        Binding("shift+down,J", "move_down", "Move down", show=True),
        Binding("shift+up,K", "move_up", "Move up", show=True),
        Binding("shift+left,H", "move_left", "Move left", show=True, priority=True),
        Binding("shift+right,L", "move_right", "Move right", show=True),
        Binding("left,h", "focus_left", "Focus left", show=False),
        Binding("right,l", "focus_right", "Focus right", show=False),
        Binding("m", "select_mode", "Select mode", show=True),
    ]
    CSS_PATH = "styles/kanban.css"

    proxy: CardProxy
    bin_proxy: BinProxy

    highlighted_card: var[CardWidget | None] = var(None)
    highlighted_bin: var[BinWidget | None] = var(None)

    @on(events.DescendantFocus)
    def handle_descendant_focus(self, message: events.DescendantFocus):
        widget = message.widget
        if isinstance(widget, CardWidget):
            self.highlighted_card = widget
        elif isinstance(widget, BinWidget):
            self.highlighted_bin = widget

    @on(events.DescendantBlur)
    def handle_descendant_blur(self, message: events.DescendantBlur):
        widget = message.widget
        if isinstance(widget, CardWidget):
            self.highlighted_card = None
        elif isinstance(widget, BinWidget):
            self.highlighted_bin = None

    def _get_focused_card(self):
        return self.query(CardWidget).first()

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
        for w in self.cont.query(BinWidget):
            w.remove()

    async def populate(self):
        cards = list(self.proxy.all())
        bin = BinWidget()
        self.cont.mount(bin)
        bin.mount_all(CardWidget(c) for c in self.proxy.all() if c.bin_id is None)

        for b in self.bin_proxy.all():
            bin = BinWidget(bin=b)
            self.cont.mount(bin)
            bin.mount_all(CardWidget(c) for c in cards if c.bin_id == b.id)

    @asynccontextmanager
    async def repopulate(self):
        async with self.batch():
            await self.clear()
            await self.populate()
            yield

    async def action_focus_left(self):
        self.focus_previous(BinWidget)

    async def action_focus_right(self):
        self.focus_next(BinWidget)

    async def _move_in_x(self, direction: Literal["left"] | Literal["right"]):
        if (bin := self.highlighted_bin) and bin.bin:
            self.bin_proxy.move(bin.bin.id, direction)
            async with self.repopulate():
                bin = bin.from_dom()
                bin.focus()
        elif card := self.highlighted_card:
            self.proxy.move(card.card.id, direction)
            async with self.repopulate():
                card = card.from_dom()
                card.focus()

    async def _move_in_y(self, direction: Literal["up"] | Literal["down"]):
        if card := self.highlighted_card:
            self.proxy.move(card.card.id, direction)
            async with self.repopulate():
                card = card.from_dom()
                card.focus()

    async def action_move_up(self):
        await self._move_in_y("up")

    async def action_move_down(self):
        await self._move_in_y("down")

    async def action_move_left(self):
        await self._move_in_x("left")

    async def action_move_right(self):
        await self._move_in_x("right")
