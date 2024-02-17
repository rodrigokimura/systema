from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    id: UUID | None = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str
    created_at: datetime = Field(default_factory=datetime.now, index=True)
