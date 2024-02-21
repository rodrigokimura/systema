from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input

from systema.server.project_manager.models.project import ProjectCreate


class CreateProjectModal(ModalScreen[ProjectCreate]):
    BINDINGS = [
        ("enter", "submit", "Submit"),
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Name", id="name")
        yield Button("Submit", "primary", id="submit")
        yield Button("Cancel", "default", id="cancel")

    def on_input_submitted(self, message: Input.Submitted):
        self.action_submit()

    def action_submit(self):
        self.notify("submit")
        self.dismiss(
            ProjectCreate(name=self.query(Input).filter("#name").only_one().value)
        )
        self.clear()

    def action_cancel(self):
        self.notify("cancel")
        self.dismiss()
        self.clear()

    def clear(self):
        for i in self.query(Input):
            i.clear()
        self.query(Input).filter("#name").only_one().focus()

    def on_button_pressed(self, message: Button.Pressed):
        actions = {"submit": self.action_submit, "cancel": self.action_cancel}
        if id := message.button.id:
            actions[id]()
