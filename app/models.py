import datetime as dt

from sqlmodel import Field, SQLModel
from zoneinfo import ZoneInfo


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


class UserBase(SQLModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


class UserPublic(UserBase):
    id: int


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None
