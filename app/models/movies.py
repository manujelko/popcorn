import datetime as dt
from zoneinfo import ZoneInfo

from sqlmodel import Field, SQLModel


def now() -> dt.datetime:
    return dt.datetime.now(tz=ZoneInfo("UTC"))


class MovieBase(SQLModel):
    title: str = Field(min_length=1)
    year: int = Field(ge=1888)
    runtime: int = Field(ge=1)


class Movie(MovieBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: dt.datetime = Field(default_factory=now)
    version: int = Field(default=1, ge=1)


class MoviePublic(MovieBase):
    id: int


class MovieCreate(MovieBase):
    pass


class MovieUpdate(SQLModel):
    title: str | None = None
    year: int | None = None
    runtime: int | None = None
