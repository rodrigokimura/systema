from sqlmodel import Field

from systema.base import BaseModel


class List(BaseModel, table=True):
    id: str = Field(..., foreign_key="project.id", primary_key=True)
