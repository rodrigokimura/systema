import typer

app = typer.Typer()


@app.command()
def serve():
    print("Command to start the server...")


if __name__ == "__main__":
    app()
