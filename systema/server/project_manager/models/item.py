from sqlmodel import Field

from systema.base import BaseModel


class Item(BaseModel, table=True):
    id: str = Field(..., foreign_key="task.id", primary_key=True)
    order: int = Field(0, ge=0)
