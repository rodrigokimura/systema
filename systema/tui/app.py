from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
)

from systema.server.project_manager.models.project import Project
from systema.tui.proxy import create_project, delete_project, get_projects
from systema.tui.screens import CreateProjectModal


class ProjectItem(Static):
    def __init__(
        self,
        project: Project,
        renderable: RenderableType = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.project = project
        super().__init__(
            renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def compose(self) -> ComposeResult:
        yield Label(self.project.name)
        yield Label(str(self.project.created_at))


class ProjectList(ListItem):
    def compose(self) -> ComposeResult:
        super().compose()
        for project in get_projects():
            yield ListItem(ProjectItem(project))


class SystemaTUIApp(App):
    TITLE = "Systema"
    BINDINGS = [
        ("q", "quit", "Quit app"),
        ("p", "add_project", "Add project"),
        ("d", "delete_project", "Delete project"),
    ]

    def compose(self) -> ComposeResult:
        self.projects = list(get_projects())
        yield Header()
        self.lv = ListView(
            *(ListItem(ProjectItem(project)) for project in get_projects())
        )
        yield self.lv
        yield Button("Add project")
        yield Footer()

    async def _populate_list_view(self):
        for project in get_projects():
            await self.lv.append(ListItem(ProjectItem(project)))

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_add_project(self):
        async def submit(project):
            proj = create_project(project)
            self.notify(f"Project created {proj.name}")
            await self.lv.clear()
            await self._populate_list_view()

        self.push_screen(CreateProjectModal(), callback=submit)
        print(self.screen_stack)

    async def action_delete_project(self):
        if item := self.lv.highlighted_child:
            project = item.query(ProjectItem).first().project
            delete_project(project.id)
            self.notify("Project deleted")
            await self.lv.clear()
            await self._populate_list_view()


if __name__ == "__main__":
    app = SystemaTUIApp()
    app.run()
