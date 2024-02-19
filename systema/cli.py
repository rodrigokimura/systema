import typer

from .__version__ import VERSION
from .management import flush as _flush
from .server.main import serve as _serve

app = typer.Typer()


@app.command(help="Start server")
def serve():
    _serve()


@app.command(help="Flush database")
def flush():
    _flush()


@app.command(help="Show version")
def version():
    print(VERSION)


if __name__ == "__main__":
    app()
