from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, ListItem

from systema.server.project_manager.models.project import (
    ProjectCreate,
    ProjectUpdate,
)
from systema.tui.proxy import ProjectProxy
from systema.tui.screens import Confirmation, ProjectModal
from systema.tui.widgets import ListView, ProjectItem


class SystemaTUIApp(App):
    TITLE = "Systema"
    BINDINGS = [
        ("q", "quit", "Quit app"),
        ("p", "add_project", "Add project"),
        ("e", "edit_project", "Edit project"),
        ("d", "delete_project", "Delete project"),
    ]

    def compose(self) -> ComposeResult:
        self.projects = list(ProjectProxy.all())
        yield Header()
        self.lv = ListView(
            *(ListItem(ProjectItem(project)) for project in ProjectProxy.all())
        )
        yield self.lv
        yield Button("Add project")
        yield Footer()

    async def _populate_list_view(self):
        for project in ProjectProxy.all():
            await self.lv.append(ListItem(ProjectItem(project)))

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    @work
    async def action_add_project(self):
        if data_for_creation := await self.push_screen_wait(ProjectModal()):
            if isinstance(data_for_creation, ProjectCreate):
                project = ProjectProxy.create(data_for_creation)
                self.notify(f"Project created {project.name}")
                await self.lv.clear()
                await self._populate_list_view()

    @work
    async def action_edit_project(self):
        if item := self.lv.highlighted_child:
            project = item.query(ProjectItem).first().project
            if data_for_update := await self.push_screen_wait(ProjectModal(project)):
                if isinstance(data_for_update, ProjectUpdate):
                    data_for_update = ProjectProxy.update(project.id, data_for_update)
                    if data_for_update:
                        self.notify(f"Project updated {data_for_update.name}")
                        await self.lv.clear()
                        await self._populate_list_view()

    @work
    async def action_delete_project(self):
        if item := self.lv.highlighted_child:
            if await self.push_screen_wait(Confirmation("Delete project?", {"d"})):
                project = item.query(ProjectItem).first().project
                ProjectProxy.delete(project.id)
                self.notify("Project deleted")
                await self.lv.clear()
                await self._populate_list_view()


if __name__ == "__main__":
    app = SystemaTUIApp()
    app.run()
