import typer
from rich import print

from systema.__version__ import VERSION
from systema.management import (
    DB_FILENAME,
    DOTENV_FILENAME,
    Settings,
)
from systema.server.auth.utils import create_superuser
from systema.server.db import create_db_and_tables
from systema.server.main import serve as _serve
from systema.tui.app import SystemaTUIApp

from .query import app as query_app

ART = r"""
  ___         _
 / __|_  _ __| |_ ___ _ __  __ _
 \__ \ || (_-<  _/ -_) '  \/ _` |
 |___/\_, /__/\__\___|_|_|_\__,_|
      |__/
"""


def print_art():
    typer.echo(ART)


app = typer.Typer(name="systema", callback=print_art, no_args_is_help=True)
app.add_typer(query_app)


@app.command()
def serve(dev: bool = typer.Option(False)):
    """Start web server"""

    _serve(dev=dev)


@app.command()
def tui(
    remote: bool = typer.Option(False, help="Enable access to remote server via HTTP"),
    dev: bool = typer.Option(False),
):
    """Start TUI client"""

    if remote:
        raise NotImplementedError("Sorry! Not available yet.")

    app = SystemaTUIApp()
    app.run()


@app.command()
def setup():
    """Run setup wizard"""
    from systema.management import settings

    if settings.check_dotenv():
        replace = typer.prompt(
            f"{DOTENV_FILENAME} found. Replace with new defaults?",
            default=True,
            type=bool,
        )
        if replace:
            settings = Settings(_env_file=None)  # type: ignore
            settings.to_dotenv()
            print(
                f"New config file generated at {settings.base_path / DOTENV_FILENAME}"
            )

    else:
        print(f"config file generated at {settings.base_path / DOTENV_FILENAME}")
        settings.to_dotenv()

    if settings.check_db():
        replace = typer.prompt(
            f"{DB_FILENAME} found. Replace with new empty database?",
            default=True,
            type=bool,
        )
        if replace:
            db_file = settings.base_path / DB_FILENAME
            db_file.unlink(missing_ok=True)
            print(f"{db_file} removed")

    create_db_and_tables()
    if typer.prompt("Create superuser?", type=bool, default=True):
        prompt_for_superuser()


def prompt_for_superuser():
    username = typer.prompt("Username", type=str)
    password = typer.prompt(
        "Password", type=str, hide_input=True, confirmation_prompt=True
    )
    create_superuser(username, password)
    print(f"Superuser {username} created")


@app.command(help="Create superuser")
def superuser():
    """Create superuser"""

    prompt_for_superuser()


@app.command(help="Show version")
def version():
    """Show version"""

    print(VERSION)
