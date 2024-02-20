import os

from sqlmodel import SQLModel, create_engine

from systema.management import settings

engine = create_engine(settings.db_address)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def drop_tables_and_db():
    SQLModel.metadata.drop_all(engine)
    sqlite_prefix = "sqlite:///"
    if settings.db_address.startswith(sqlite_prefix):
        db_file = settings.db_address.split(sqlite_prefix)[-1]
        os.remove(db_file)


def show_tables():
    print(SQLModel.metadata.tables)
