import enum

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class Mode(str, enum.Enum):
    CHECKLIST = "list"
    KANBAN = "kanban"
    TIMELINE = "timeline"
    CALENDAR = "calendar"


class ModeModal(ModalScreen[Mode]):
    CSS_PATH = "styles/mode-modal.css"
    BINDINGS = [
        Binding("escape", "dismiss", "Dismiss"),
        Binding("up,k", "focus_previous", "Focus previous", show=False),
        Binding("down,j", "focus_next", "Focus next", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Modes")
            for mode in Mode:
                yield Button(mode.name, id=mode.value)

    @on(Button.Pressed)
    async def handle_button_pressed(self, message: Button.Pressed):
        message.stop()
        mode = message.button.id
        if mode:
            self.dismiss(Mode(mode))
