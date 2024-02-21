from sqlmodel import Session, select

from systema.server.db import engine
from systema.server.project_manager.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
)


class ProjectProxy:
    @staticmethod
    def all():
        with Session(engine) as session:
            statement = select(Project)
            projects = session.exec(statement).all()
            return projects

    @staticmethod
    def create(data: ProjectCreate):
        return Project.create(data)

    @staticmethod
    def update(id: str, data: ProjectUpdate):
        return Project.update(id, data)

    @staticmethod
    def delete(id: str):
        Project.delete(id)
