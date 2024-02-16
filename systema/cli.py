import typer

from .__version__ import VERSION

app = typer.Typer()


@app.command()
def serve():
    print("Command to start the server...")


@app.command()
def version():
    print(VERSION)


if __name__ == "__main__":
    app()
