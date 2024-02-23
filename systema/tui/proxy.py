from systema.server.project_manager.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
)


class ProjectProxy:
    @staticmethod
    def all():
        return Project.list()

    @staticmethod
    def create(data: ProjectCreate):
        return Project.create(data)

    @staticmethod
    def update(id: str, data: ProjectUpdate):
        return Project.update(id, data)

    @staticmethod
    def delete(id: str):
        Project.delete(id)
