from contextlib import asynccontextmanager

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer, Header, ListItem

from systema.server.project_manager.models.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from systema.tui.proxy import ProjectProxy
from systema.tui.screens.confirmation import Confirmation
from systema.tui.screens.project_modal import ProjectModal
from systema.tui.widgets import ListView, ProjectItem


class ProjectList(Screen):
    BINDINGS = [
        Binding("q,escape", "dismiss", "Quit", show=True),
        Binding("a", "add_project", "Add", show=True),
        Binding("e", "edit_project", "Edit", show=True),
        Binding("d", "delete_project", "Delete", show=True),
    ]
    CSS_PATH = "styles/project-list.css"

    class Selected(Message):
        def __init__(self, project: ProjectRead) -> None:
            super().__init__()
            self.project = project

    def compose(self) -> ComposeResult:
        self.proxy = ProjectProxy()
        self.list_view = ListView()
        yield Header()
        yield self.list_view
        yield Footer()

    async def on_mount(self):
        await self._populate_list_view()

    def get_highlighted_project(self):
        item = self.list_view.highlighted_child
        if item is None:
            raise ValueError()
        project_item = item.query_one(ProjectItem)
        project = project_item.project
        if project is None:
            raise ValueError()
        return project_item, project

    async def _populate_list_view(self):
        for project in self.proxy.all():
            project_item = ProjectItem()
            project_item.project = project
            self.list_view.append(ListItem(project_item))

    @asynccontextmanager
    async def repopulate(self):
        async with self.batch():
            await self.list_view.clear()
            await self._populate_list_view()
            yield

    @work
    async def action_add_project(self):
        data_for_creation = await self.app.push_screen_wait(ProjectModal())
        if not isinstance(data_for_creation, ProjectCreate):
            return
        created_project = self.proxy.create(data_for_creation)
        self.notify(f"Project created {created_project.name}")
        async with self.repopulate():
            pass

    @work
    async def action_edit_project(self):
        item, project = self.get_highlighted_project()
        data_for_update = await self.app.push_screen_wait(ProjectModal(project))
        if not isinstance(data_for_update, ProjectUpdate):
            return
        updated_project = self.proxy.update(project.id, data_for_update)
        self.notify(f"Project updated {updated_project.name}")
        item.project = updated_project

    @work
    async def action_delete_project(self):
        _, project = self.get_highlighted_project()
        current_index = self.list_view.index
        if await self.app.push_screen_wait(Confirmation("Delete project?", {"d"})):
            self.proxy.delete(project.id)
            self.notify("Project deleted")
            async with self.repopulate():
                self.list_view.index = current_index

    @on(ListView.Selected)
    def handle_item_selected(self, message: ListView.Selected):
        project = message.item.query_one(ProjectItem).project
        if project:
            new_message = self.Selected(project)
            new_message.project = project
            self.post_message(new_message)
