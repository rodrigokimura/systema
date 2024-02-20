from sqlmodel import Field, SQLModel

from systema.management import settings
from systema.security import generate_id


class BaseTableModel(SQLModel):
    id: str = Field(
        default_factory=generate_id,
        primary_key=True,
        index=True,
        nullable=False,
        min_length=settings.nanoid_size,
        max_length=settings.nanoid_size,
    )
