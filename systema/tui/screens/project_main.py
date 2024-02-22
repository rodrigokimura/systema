import enum

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Label

from systema.server.project_manager.models.project import Project

from ..widgets import Select


class Mode(str, enum.Enum):
    LIST = "list"
    KANBAN = "kanban"
    TIMELINE = "timeline"
    CALENDAR = "calendar"


class ProjectMain(Screen):
    BINDINGS = [
        Binding("q,escape", "dismiss", "Dismiss"),
        Binding("up,k", "focus_previous", "Focus previous", show=False),
        Binding("down,j", "focus_next", "Focus next", show=False),
    ]
    CSS_PATH = "styles/project-main.css"

    def __init__(
        self,
        project: Project | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.project = project
        super().__init__(name, id, classes)

    def compose(self) -> ComposeResult:
        yield Header()
        modes = Select(
            ((m.name.title(), m) for m in Mode),
            value="calendar",
        )
        yield modes
        if self.project:
            yield Label(self.project.id)
            yield Label(self.project.name)
        yield Footer()
