from __future__ import annotations

from typing import ClassVar

from sqlmodel import Field
from sqlmodel import SQLModel as _SQLModel

from systema.management import settings
from systema.security import generate_id


class BaseModel(_SQLModel):
    __plural__: ClassVar[str | None] = None
    """Custom plural"""

    class NotFound(Exception):
        ...

    @classmethod
    def get_singular_name(cls):
        return cls.__name__

    @classmethod
    def get_plural_name(cls):
        if plural := cls.__plural__:
            return plural
        return cls.get_singular_name() + "s"


class IdMixin(_SQLModel):
    id: str = Field(
        default_factory=generate_id,
        primary_key=True,
        index=True,
        nullable=False,
        min_length=settings.nanoid_size,
        max_length=settings.nanoid_size,
    )
