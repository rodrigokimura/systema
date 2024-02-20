import typer

from systema.server.auth.utils import create_superuser
from systema.server.db import drop_tables_and_db, show_tables

from .__version__ import VERSION
from .server.main import serve as _serve

app = typer.Typer()


@app.command(help="Start server")
def serve(dev: bool = typer.Option(False)):
    _serve(dev=dev)


@app.command(help="Create superuser")
def superuser(
    username: str = typer.Option(prompt="Username"),
    password: str = typer.Option(
        prompt="Password", confirmation_prompt=True, hide_input=True
    ),
):
    create_superuser(username, password)


@app.command(help="Show version")
def version():
    print(VERSION)


@app.command(help="Show tables")
def tables():
    show_tables()


@app.command(help="Drop tables")
def drop():
    drop_tables_and_db()


if __name__ == "__main__":
    app()
