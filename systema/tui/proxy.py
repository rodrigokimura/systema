from sqlmodel import Session, select

from systema.server.db import engine
from systema.server.project_manager.models.project import Project, ProjectCreate


def get_projects():
    with Session(engine) as session:
        statement = select(Project)
        projects = session.exec(statement).all()
        return projects


def create_project(data: ProjectCreate):
    return Project.create(data)


def delete_project(id: str):
    Project.delete(id)
