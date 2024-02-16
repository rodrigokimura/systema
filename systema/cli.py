import typer

from .__version__ import VERSION
from .server.main import serve as _serve

app = typer.Typer()


@app.command()
def serve():
    print("Command to start the server...")
    _serve()


@app.command()
def version():
    print(VERSION)


if __name__ == "__main__":
    app()
