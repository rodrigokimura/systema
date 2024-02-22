from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class Confirmation(ModalScreen[bool]):
    CSS_PATH = "styles/confirmation.css"
    BINDINGS = [
        ("escape", "cancel", None),
        ("l", "focus_next", None),
        ("j", "focus_next", None),
        ("h", "focus_previous", None),
        ("k", "focus_previous", None),
    ]
    AUTO_FOCUS = "#confirm"

    def __init__(
        self,
        message: str,
        extra_bindings_for_confirm: set[str] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.message = message
        self.extra_bindings = extra_bindings_for_confirm or set()
        super().__init__(name, id, classes)

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.message),
            Button("Cancel", "default", id="cancel"),
            Button("Confirm", "primary", id="confirm"),
        )

    def action_confirm(self):
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)

    @on(Button.Pressed)
    def process_pressed_event(self, message: Button.Pressed):
        actions = {"confirm": self.action_confirm, "cancel": self.action_cancel}
        if id := message.button.id:
            actions[id]()

    def on_key(self, event: Key):
        if event.key in self.extra_bindings:
            self.action_confirm()
