from textual import on, work
from textual.app import App, UnknownModeError
from textual.binding import Binding
from textual.reactive import var

from systema.server.project_manager.models.project import ProjectRead
from systema.tui.proxy import ItemProxy
from systema.tui.screens.base import ProjectScreen
from systema.tui.screens.dashboard import Dashboard
from systema.tui.screens.list_main import ListScreen
from systema.tui.screens.mode_modal import Mode, ModeModal
from systema.tui.screens.project_list import ProjectList

PROJECT_SCREENS: dict[Mode, ProjectScreen] = {
    Mode.LIST: ListScreen(ItemProxy),
}


class SystemaTUIApp(App):
    TITLE = "Systema"
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("escape", "quit", "Quit", show=True),
        Binding("up,k", "focus_previous", "Focus previous", show=False),
        Binding("down,j", "focus_next", "Focus next", show=False),
        Binding("m", "select_mode", "Select mode", show=True),
    ]
    CSS_PATH = "style.css"
    SCREENS = {
        "projects": ProjectList(),
        "mode": ModeModal(),
        **PROJECT_SCREENS,
    }
    MODES = {"main": Dashboard(), **PROJECT_SCREENS}
    project: var[ProjectRead | None] = var(None)

    def on_mount(self):
        self.switch_mode("main")

    def watch_project(self, project: ProjectRead | None):
        for mode in Mode:
            if screen := PROJECT_SCREENS.get(mode):
                screen.project = project

    @on(ProjectList.Selected)
    async def handle_project_selection(self, message: ProjectList.Selected):
        project = message.project
        self.project = project
        await self.run_action("select_mode")

    @work
    async def action_select_mode(self):
        if self.project:
            mode = await self.push_screen_wait("mode")
            try:
                self.switch_mode(mode)
            except UnknownModeError:
                self.notify("Mode not implemented yet", severity="error")


if __name__ == "__main__":
    app = SystemaTUIApp()
    app.run()
