from textual import on
from textual.app import App
from textual.binding import Binding

from systema.tui.screens.dashboard import Dashboard
from systema.tui.screens.project_list import ProjectList
from systema.tui.screens.project_main import ProjectMain


class SystemaTUIApp(App):
    TITLE = "Systema"
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("escape", "quit", "Quit", show=True),
        Binding("up", "focus_previous", "Focus previous", show=False),
        Binding("down", "focus_next", "Focus next", show=False),
        Binding("k", "focus_previous", "Focus previous", show=False),
        Binding("j", "focus_next", "Focus next", show=False),
    ]
    SCREENS = {
        "dashboard": Dashboard(),
        "projects": ProjectList(),
        "project": ProjectMain(),
    }

    def on_mount(self):
        self.push_screen("dashboard")

    @on(ProjectList.Selected)
    def handle_project_selection(self, message: ProjectList.Selected):
        self.push_screen(ProjectMain(message.project))


if __name__ == "__main__":
    app = SystemaTUIApp()
    app.run()
