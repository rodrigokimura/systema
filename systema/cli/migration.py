from sqlmodel import Session, select

from systema.models.board import Board
from systema.models.card import Card
from systema.models.checklist import Checklist
from systema.models.item import Item
from systema.models.project import Project, SubProjectMixin
from systema.models.task import SubTaskMixin, Task
from systema.server.db import engine

CoreModels = Project | Task
SubModels = SubProjectMixin | SubTaskMixin


def create_submodels():
    submodels_by_core_model: dict[type[CoreModels], tuple[type[SubModels], ...]] = {
        Project: (
            Checklist,
            Board,
        ),
        Task: (Item, Card),
    }

    with Session(engine) as session:
        for core_model, submodels in submodels_by_core_model.items():
            print(f"Iterating through {core_model.__name__}")
            for core_instance in session.exec(select(core_model)).all():
                for submodel in submodels:
                    if not session.get(submodel, core_instance.id):
                        print(
                            f"Instance of {submodel.__name__} not found for id={core_instance.id}"
                        )
                        session.add(submodel(id=core_instance.id))
                        session.commit()
