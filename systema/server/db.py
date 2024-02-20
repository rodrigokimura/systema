from sqlmodel import SQLModel, create_engine

from systema.management import settings

engine = create_engine(settings.db_address)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def show_tables():
    print(SQLModel.metadata.tables)
