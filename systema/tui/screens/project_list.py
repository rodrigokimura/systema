from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer, Header, ListItem

from systema.server.project_manager.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
)
from systema.tui.proxy import ProjectProxy
from systema.tui.screens.confirmation import Confirmation
from systema.tui.screens.project_modal import ProjectModal
from systema.tui.widgets import ListView, ProjectItem


class ProjectList(Screen):
    BINDINGS = [
        Binding("q", "dismiss", "Dismiss"),
        Binding("escape", "dismiss", "Dismiss"),
        Binding("p", "add_project", "Add project"),
        Binding("e", "edit_project", "Edit project"),
        Binding("d", "delete_project", "Delete project"),
    ]
    CSS_PATH = "styles/project-list.css"

    class Selected(Message):
        def __init__(self, project: Project) -> None:
            super().__init__()
            self.project: Project = project

    def compose(self) -> ComposeResult:
        self.projects = list(ProjectProxy.all())
        yield Header()
        self.list_view = ListView(
            *(ListItem(ProjectItem(project)) for project in ProjectProxy.all())
        )
        yield self.list_view
        yield Footer()

    def get_highlighted_project(self):
        if item := self.list_view.highlighted_child:
            return item.query(ProjectItem).first().project

    async def _populate_list_view(self):
        for project in ProjectProxy.all():
            await self.list_view.append(ListItem(ProjectItem(project)))

    @work
    async def action_add_project(self):
        if data_for_creation := await self.app.push_screen_wait(ProjectModal()):
            if isinstance(data_for_creation, ProjectCreate):
                project = ProjectProxy.create(data_for_creation)
                self.notify(f"Project created {project.name}")
                await self.list_view.clear()
                await self._populate_list_view()

    @work
    async def action_edit_project(self):
        if project := self.get_highlighted_project():
            if data_for_update := await self.app.push_screen_wait(
                ProjectModal(project)
            ):
                if isinstance(data_for_update, ProjectUpdate):
                    data_for_update = ProjectProxy.update(project.id, data_for_update)
                    if data_for_update:
                        self.notify(f"Project updated {data_for_update.name}")
                        await self.list_view.clear()
                        await self._populate_list_view()

    @work
    async def action_delete_project(self):
        if project := self.get_highlighted_project():
            if await self.app.push_screen_wait(Confirmation("Delete project?", {"d"})):
                ProjectProxy.delete(project.id)
                self.notify("Project deleted")
                await self.list_view.clear()
                await self._populate_list_view()

    @on(ListView.Selected)
    def handle_item_selected(self, message: ListView.Selected):
        project = message.item.query(ProjectItem).first().project
        self.post_message(self.Selected(project))
