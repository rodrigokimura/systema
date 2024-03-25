from contextlib import asynccontextmanager
from typing import Literal

from textual import work
from textual.app import ComposeResult, events, on
from textual.binding import Binding
from textual.containers import HorizontalScroll
from textual.reactive import var
from textual.widgets import Footer, Header

from systema.models.bin import BinCreate, BinUpdate
from systema.models.card import CardCreate, CardUpdate
from systema.models.project import ProjectRead
from systema.tui.proxy import BinProxy, CardProxy
from systema.tui.screens.base import ProjectScreen
from systema.tui.screens.bin_modal import BinModal
from systema.tui.screens.card_modal import CardModal
from systema.tui.screens.confirmation import Confirmation
from systema.tui.widgets import Bin as BinWidget
from systema.tui.widgets import Card as CardWidget


class KanbanScreen(ProjectScreen):
    BINDINGS = [
        Binding("q,escape", "dismiss", "Quit", show=True),
        Binding("a", "add", "Add", show=True),
        Binding("e", "edit", "Edit", show=True),
        Binding("d", "delete", "Delete", show=True),
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

    board = HorizontalScroll()

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
        yield self.board
        yield Footer()

    async def clear(self):
        self.highlighted_bin = None
        self.highlighted_card = None
        self.board.focus()
        for bin in self.board.query(BinWidget):
            bin.remove()

    async def populate(self):
        cards = list(self.proxy.all())
        bin = BinWidget()
        self.board.mount(bin)
        bin.mount_all(CardWidget(c) for c in self.proxy.all() if c.bin_id is None)

        for bin_ in self.bin_proxy.all():
            bin = BinWidget(bin=bin_)
            self.board.mount(bin)
            bin.mount_all(CardWidget(c) for c in cards if c.bin_id == bin_.id)

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
        elif (card := self.highlighted_card) and card.card:
            self.proxy.move(card.card.id, direction)
            async with self.repopulate():
                card = card.from_dom()
                card.focus()

    async def _move_in_y(self, direction: Literal["up"] | Literal["down"]):
        if (card := self.highlighted_card) and card.card:
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

    @work
    async def action_add(self):
        if not self.highlighted_bin and not self.highlighted_card:
            bin_modal = BinModal()
            data_for_creation = await self.app.push_screen_wait(bin_modal)
            if not isinstance(data_for_creation, BinCreate):
                return
            created_bin = self.bin_proxy.create(data_for_creation)
            self.notify(f"Bin created {created_bin.name}")
            async with self.repopulate():
                bin = BinWidget.by_id(self.app, created_bin.id)
                bin.focus()
        else:
            bin = self.highlighted_bin
            if bin and bin.bin:
                card_modal = CardModal(bin_id=bin.bin.id)
            else:
                card_modal = CardModal()

            data_for_creation = await self.app.push_screen_wait(card_modal)
            if not isinstance(data_for_creation, CardCreate):
                return
            created_card = self.proxy.create(data_for_creation)
            self.notify(f"Card created {created_card.name}")
            async with self.repopulate():
                card = CardWidget.by_id(self.app, created_card.id)
                card.focus()

    @work
    async def action_edit(self):
        if (bin := self.highlighted_bin) and bin.bin:
            data_for_update = await self.app.push_screen_wait(BinModal(bin.bin))
            if not isinstance(data_for_update, BinUpdate):
                return
            updated_item = self.bin_proxy.update(bin.bin.id, data_for_update)
            self.notify(f"Bin updated {updated_item.name}")
            bin.bin = updated_item
        elif (card := self.highlighted_card) and card.card:
            data_for_update = await self.app.push_screen_wait(CardModal(card.card))
            if not isinstance(data_for_update, CardUpdate):
                return
            updated_item = self.proxy.update(card.card.id, data_for_update)
            self.notify(f"Card updated {updated_item.name}")
            card.card = updated_item

    @work
    async def action_delete(self):
        if (bin := self.highlighted_bin) and bin.bin:
            if await self.app.push_screen_wait(Confirmation("Delete bin?")):
                self.bin_proxy.delete(bin.bin.id)
                self.notify("Bin deleted")
                async with self.repopulate():
                    pass
        elif (card := self.highlighted_card) and card.card:
            if await self.app.push_screen_wait(Confirmation("Delete card?")):
                self.proxy.delete(card.card.id)
                self.notify("Card deleted")
                async with self.repopulate():
                    pass

    def dismiss(self, result=None):
        if (
            self.highlighted_card
            and self.highlighted_card.parent
            and isinstance(self.highlighted_card.parent, BinWidget)
        ):
            self.highlighted_card.parent.focus()
        elif self.highlighted_bin:
            self.board.focus()
        else:
            return super().dismiss(result)
