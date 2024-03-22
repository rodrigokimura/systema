from sqlmodel import Field

from systema.base import BaseModel


class Checklist(BaseModel, table=True):
    id: str = Field(..., foreign_key="project.id", primary_key=True)
