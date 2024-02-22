from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from systema.server.project_manager.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
)


class ProjectModal(ModalScreen[ProjectCreate | ProjectUpdate]):
    CSS_PATH = "styles/project-modal.css"
    BINDINGS = [
        ("enter", "submit", "Submit"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        project: Project | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.project = project
        self.form_data = {}
        super().__init__(name, id, classes)

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Project"),
            Input(
                placeholder="Name",
                id="name",
                name="name",
                value=self.project.name if self.project else "",
            ),
            Button("Cancel", "default", id="cancel"),
            Button("Submit", "primary", id="submit"),
        )

    def action_submit(self):
        if self.project:
            changed_data = ProjectUpdate(**self.form_data)
            original_data = ProjectUpdate.model_validate(self.project)
            if changed_data == original_data:
                self.notify("Nothing to update")
                self.dismiss()
                return
            return_value = changed_data
        else:
            return_value = ProjectCreate(
                name=self.query(Input).filter("#name").only_one().value
            )
        self.notify("Submitted")
        self.dismiss(return_value)
        self.clear()

    def action_cancel(self):
        self.notify("Canceled")
        self.dismiss()
        self.clear()

    def clear(self):
        for i in self.query(Input):
            i.clear()
        self.query(Input).filter("#name").only_one().focus()

    @on(Input.Changed)
    def handle_input_changed(self, message: Input.Changed):
        self.form_data[message.input.name] = message.value

    @on(Input.Submitted)
    def handle_input_submitted(self, message: Input.Submitted):
        print(f"Input submitted {message.input}")
        self.action_submit()

    @on(Button.Pressed)
    def handle_button_pressed(self, message: Button.Pressed):
        actions = {"submit": self.action_submit, "cancel": self.action_cancel}
        if id := message.button.id:
            actions[id]()
