from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header


class Dashboard(Screen[None]):
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("p", "projects", "Projects", show=True),
    ]
    CSS_PATH = "styles/dashboard.css"

    def compose(self) -> ComposeResult:
        users = Button("Users")
        projects = Button("Projects")
        config = Button("Config")
        self.buttons_and_actions = {
            projects: self.action_projects,
        }
        yield Header()
        yield Vertical(users, projects, config, classes="buttons")
        yield Footer()

    def action_projects(self):
        self.app.push_screen("projects")

    @on(Button.Pressed)
    def handle_button_pressed(self, message: Button.Pressed):
        if action := self.buttons_and_actions.get(message.button):
            return action()
        self.notify("Button not implemented yet", severity="error")
