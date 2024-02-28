from contextlib import asynccontextmanager
from typing import Literal

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Collapsible, Footer, Header, ListItem

from systema.server.project_manager.models.item import ItemCreate, ItemUpdate
from systema.server.project_manager.models.task import Status
from systema.tui.proxy import ItemProxy
from systema.tui.screens.base import ProjectScreen
from systema.tui.screens.confirmation import Confirmation
from systema.tui.screens.item_modal import ItemModal
from systema.tui.widgets import Item, ListView


class ListScreen(ProjectScreen):
    BINDINGS = [
        Binding("q,escape", "dismiss", "Quit"),
        Binding("a", "add_item", "Add", show=True),
        Binding("e", "edit_item", "Edit", show=True),
        Binding("d", "delete_item", "Delete", show=True),
        Binding("ctrl+down,ctrl+j", "move_down", "Move down", show=True),
        Binding("ctrl+up,ctrl+k", "move_up", "Move up", show=True),
        Binding("space,enter", "toggle_item", "Check/Uncheck", show=True),
        Binding("t", "toggle_collapsible", "Show/Hide completed", show=True),
        Binding("m", "select_mode", "Select mode", show=True),
    ]
    CSS_PATH = "styles/list-main.css"

    current_item: var[Item | None] = var(None)
    proxy: ItemProxy

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            if self.project:
                self.unchecked_items = ListView()
                self.checked_items = ListView()
                yield self.unchecked_items
            self.collapsible = Collapsible(self.checked_items, title="Completed items")
            yield self.collapsible
        yield Footer()

    @asynccontextmanager
    async def repopulate(self):
        focus_checked = self.checked_items.has_focus
        focus_unchecked = self.unchecked_items.has_focus
        checked_idx = self.checked_items.index
        unchecked_idx = self.unchecked_items.index
        async with self.batch():
            await self.clear()
            await self.populate()
            if focus_checked:
                self.checked_items.index = checked_idx
            if focus_unchecked:
                self.unchecked_items.index = unchecked_idx
            yield

    async def clear(self):
        await self.unchecked_items.clear()
        await self.checked_items.clear()

    async def populate(self):
        for item in self.proxy.all():
            i = Item()
            i.item = item
            if item.status == Status.DONE:
                await self.checked_items.append(ListItem(i))
            else:
                await self.unchecked_items.append(ListItem(i))

    def get_highlighted_item(self):
        item = self.current_item
        if item is None:
            raise ValueError()
        item_read = item.item
        if item_read is None:
            raise ValueError()
        return item, item_read

    @work
    async def action_add_item(self):
        data_for_creation = await self.app.push_screen_wait(ItemModal())
        if not isinstance(data_for_creation, ItemCreate):
            return
        created_item = self.proxy.create(data_for_creation)
        self.notify(f"Item created {created_item.name}")
        async with self.repopulate():
            self.unchecked_items.index = 0

    @work
    async def action_edit_item(self):
        item, item_read = self.get_highlighted_item()
        data_for_update = await self.app.push_screen_wait(ItemModal(item_read))
        if not isinstance(data_for_update, ItemUpdate):
            return
        updated_item = self.proxy.update(item_read.id, data_for_update)
        self.notify(f"Item updated {updated_item.name}")
        item.item = updated_item

    @work
    async def action_delete_item(self):
        _, item_read = self.get_highlighted_item()
        current_index = self.unchecked_items.index
        if await self.app.push_screen_wait(Confirmation("Delete item?", {"d"})):
            self.proxy.delete(item_read.id)
            self.notify("Item deleted")
            async with self.repopulate():
                self.unchecked_items.index = current_index

    async def action_move_down(self):
        await self._move("down")

    async def action_move_up(self):
        await self._move("up")

    async def _move(self, up_or_down: Literal["up"] | Literal["down"]):
        if self.checked_items.has_focus:
            return
        _, item_read = self.get_highlighted_item()
        current_index = self.unchecked_items.index
        self.proxy.move(item_read.id, up_or_down)
        async with self.repopulate():
            if current_index is not None:
                if up_or_down == "up":
                    self.unchecked_items.index = current_index - 1
                elif up_or_down == "down":
                    self.unchecked_items.index = current_index + 1

    async def action_toggle_item(self):
        item, _ = self.get_highlighted_item()
        item.checkbox.value = not item.checkbox.value

    @on(Item.Changed)
    async def handle_item_changed(self, message: Item.Changed):
        item_read = message.item
        item_read = self.proxy.toggle(item_read.id)
        async with self.repopulate():
            pass

    @on(ListView.Highlighted)
    async def handle_listview_highlighted(self, message: ListView.Highlighted):
        if message.item:
            try:
                self.current_item = message.item.query_one(Item)
            except NoMatches:
                pass

    @on(ListView.Focus)
    async def handle_listview_focus(self, message: ListView.Focus):
        if list_item := message.list_view.highlighted_child:
            self.current_item = list_item.query_one(Item)

    async def action_toggle_collapsible(self):
        self.collapsible.collapsed = not self.collapsible.collapsed
        if self.collapsible.collapsed:
            self.unchecked_items.focus()
        else:
            self.checked_items.focus()
