import pyperclip
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Input, Label, Pretty, Switch

from systema.management import settings


class Config(Screen[None]):
    BINDINGS = [
        Binding("q,escape", "quit", "Quit", show=True),
    ]
    CSS_PATH = "styles/config.css"

    def compose(self) -> ComposeResult:
        self.secret_key = Input(settings.secret_key, password=True, disabled=True)
        self.secret_key_switch = Switch(False, id="secret-key-switch")
        self.secret_key_copy = Button("Copy", id="secret-key-copy")
        with VerticalScroll():
            yield Label("Secret Key", shrink=True)
            with Horizontal():
                yield self.secret_key
                yield self.secret_key_switch
                yield self.secret_key_copy

            self.access_token_expiry = Input(
                str(settings.access_token_expire_minutes), disabled=True
            )
            yield Label("Access Token Expiry (in minutes)")
            yield self.access_token_expiry
            yield Pretty(settings.model_dump())

        yield Footer()

    @on(Switch.Changed, "#secret-key-switch")
    def toggle_secret_key_visibility(self, message: Switch.Changed):
        self.secret_key.password = not message.value

    @on(Button.Pressed, "#secret-key-copy")
    def copy_secret_key(self, _: Button.Pressed):
        pyperclip.copy(self.secret_key.value)

        self.notify("Secret Key copied!")

    def action_quit(self):
        self.app.switch_mode("main")
