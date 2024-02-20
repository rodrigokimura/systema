from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class SystemaTUIApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit app"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark


if __name__ == "__main__":
    app = SystemaTUIApp()
    app.run()
