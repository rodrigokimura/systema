from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, ListItem

from systema.server.project_manager.models.item import ItemCreate, ItemUpdate
from systema.server.project_manager.models.project import ProjectRead
from systema.tui.proxy import ItemProxy
from systema.tui.screens.confirmation import Confirmation
from systema.tui.screens.item_modal import ItemModal
from systema.tui.widgets import Item, ListView


class ListMain(Screen):
    BINDINGS = [
        Binding("q,escape", "dismiss", "Dismiss"),
        Binding("up,k", "focus_previous", "Focus previous", show=False),
        Binding("down,j", "focus_next", "Focus next", show=False),
        Binding("a", "add_item", "Add item", show=True),
        Binding("e", "edit_item", "Edit item", show=True),
        Binding("d", "delete_item", "Delete item", show=True),
        Binding("ctrl+down,ctrl+j", "move_down", "Move item down", show=True),
        Binding("ctrl+up,ctrl+k", "move_up", "Move item up", show=True),
        Binding("space,enter", "toggle_item", "Toggle item", show=True),
    ]
    CSS_PATH = "styles/list-main.css"

    def __init__(
        self,
        project: ProjectRead | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.project = project
        if self.project:
            self.proxy = ItemProxy(self.project.id)
        super().__init__(name, id, classes)

    def compose(self) -> ComposeResult:
        yield Header()
        if self.project:
            self.list_view = ListView(
                *(ListItem(Item(item)) for item in self.proxy.all())
            )
            yield self.list_view
        yield Footer()

    async def _populate_list_view(self):
        for item in self.proxy.all():
            await self.list_view.append(ListItem(Item(item)))

    def get_highlighted_item(self):
        if item := self.list_view.highlighted_child:
            return item.query(Item).first().item

    @work
    async def action_add_item(self):
        if data_for_creation := await self.app.push_screen_wait(ItemModal()):
            if isinstance(data_for_creation, ItemCreate):
                item = self.proxy.create(data_for_creation)
                self.notify(f"Item created {item.name}")
                await self.list_view.clear()
                await self._populate_list_view()

    @work
    async def action_edit_item(self):
        if item := self.get_highlighted_item():
            current_index = self.list_view.index
            if data_for_update := await self.app.push_screen_wait(ItemModal(item)):
                if isinstance(data_for_update, ItemUpdate):
                    data_for_update = self.proxy.update(item.id, data_for_update)
                    if data_for_update:
                        self.notify(f"Item updated {data_for_update.name}")
                        await self.list_view.clear()
                        await self._populate_list_view()
                        self.list_view.index = current_index

    @work
    async def action_delete_item(self):
        if item := self.get_highlighted_item():
            current_index = self.list_view.index
            if await self.app.push_screen_wait(Confirmation("Delete item?", {"d"})):
                self.proxy.delete(item.id)
                self.notify("Item deleted")
                await self.list_view.clear()
                await self._populate_list_view()
                self.list_view.index = current_index

    async def action_move_down(self):
        if item := self.get_highlighted_item():
            i = self.proxy.move(item.id, "down")
            await self.list_view.clear()
            await self._populate_list_view()
            self.list_view.index = i.order

    async def action_move_up(self):
        if item := self.get_highlighted_item():
            i = self.proxy.move(item.id, "up")
            await self.list_view.clear()
            await self._populate_list_view()
            self.list_view.index = i.order

    async def action_toggle_item(self):
        if child := self.list_view.highlighted_child:
            item = child.query(Item).first()
            i = self.proxy.toggle(item.item.id)
            item.checkbox.value = i.is_done()
