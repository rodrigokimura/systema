import typer

from systema.management import (
    DB_FILENAME,
    DOTENV_FILENAME,
    Settings,
)
from systema.server.auth.utils import create_superuser
from systema.server.db import create_db_and_tables, show_tables

from .__version__ import VERSION
from .server.main import serve as _serve

app = typer.Typer()


@app.command(help="Start server")
def serve(dev: bool = typer.Option(False)):
    _serve(dev=dev)


@app.command(help="Run setup wizard")
def setup():
    from systema.management import settings

    if settings.check_dotenv():
        replace = typer.prompt(
            f"{DOTENV_FILENAME} found. Replace with new defaults?",
            default=True,
            type=bool,
        )
        if replace:
            new_settings = Settings(_env_file=None)  # type: ignore
            new_settings.to_dotenv()
            print(f"New config file generated at {new_settings.base_path / '.env'}")
            settings = new_settings

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
    prompt_for_superuser()


@app.command(help="Show version")
def version():
    print(VERSION)


@app.command(help="Show tables")
def tables():
    show_tables()


if __name__ == "__main__":
    app()
