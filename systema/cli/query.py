import typer
from pydantic_core import PydanticUndefined
from rich import print
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from systema.base import BaseModel
from systema.server.auth.models import User
from systema.server.auth.utils import get_hash
from systema.server.project_manager.models.item import Item
from systema.server.project_manager.models.list import List
from systema.server.project_manager.models.project import Project
from systema.server.project_manager.models.task import Task


def all(model_class: type[BaseModel]):
    table = get_table(model_class)
    console = Console()
    console.print(table)


def add(model_class: type[BaseModel]):
    from systema.server.db import engine

    data = {}
    for name, info in model_class.model_fields.items():
        expected_type = info.annotation
        has_default_factory = info.default_factory is not None
        if expected_type and not has_default_factory:
            default_value = (
                info.default if info.default is not PydanticUndefined else None
            )

            # handle special case for hashed fields
            hashed_field_prefix = "hashed_"
            is_hashed_field = name.startswith(hashed_field_prefix)

            prompt = f"{name[len(hashed_field_prefix):] if is_hashed_field else name} [type={expected_type.__name__}]"
            if default_value is not None:
                prompt += f" [default={default_value}]"

            # handle special case for foreign keys
            # TODO: figure out a way to validate related tables
            # fk: str | None = getattr(info, "foreign_key", None)
            # if fk:
            #     fk_table, fk_field = fk.split(".")
            #     SQLModel.metadata.tables[fk_table]

            value = typer.prompt(
                prompt,
                type=expected_type,
                confirmation_prompt=is_hashed_field,
                hide_input=is_hashed_field,
                default=default_value,
                show_default=False,
                show_choices=True,
            )
            data[name] = get_hash(value) if is_hashed_field else value

    model_instance = model_class(**data)

    with Session(engine) as session:
        session.add(model_instance)
        session.commit()
        session.refresh(model_instance)

    print(f"[bold green]{model_class.get_singular_name()} created![/bold green]")
    print(model_instance)


def app_factory(model_class: type[BaseModel]):
    model_name = model_class.get_singular_name().lower()
    model_name_plural = model_class.get_plural_name().lower()
    model_app = typer.Typer(
        name=model_name_plural, help=f"Query {model_name_plural}", no_args_is_help=True
    )

    model_app.command(name="all", help=f"List all {model_name_plural}")(
        lambda: all(model_class)
    )
    model_app.command(name="add", help=f"Add {model_name}")(lambda: add(model_class))

    return model_app


def add_model_app(parent: typer.Typer, model_class: type[BaseModel]):
    child_app = app_factory(model_class)
    parent.add_typer(child_app)


def get_table(model_class: type[BaseModel]):
    from systema.server.db import engine

    statement = select(model_class)
    with Session(engine) as session:
        users = session.exec(statement).all()
    table = Table(title=model_class.get_plural_name())

    fields = list(model_class.model_fields)
    for field in fields:
        table.add_column(field)
    for user in users:
        table.add_row(*(str(getattr(user, field)) for field in fields))
    return table


app = typer.Typer(name="query", no_args_is_help=True)

add_model_app(app, User)

add_model_app(app, Project)
add_model_app(app, Task)

add_model_app(app, List)
add_model_app(app, Item)
