import datetime as dt
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from sqlmodel import Field, Session, SQLModel, create_engine, select
from zoneinfo import ZoneInfo

version = "1.0.0"
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


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


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/v1/healthcheck")
async def healthcheck() -> dict[str, str]:
    """Show application information."""
    return {"status": "available", "version": version}


@app.get("/v1/movies", response_model=list[MoviePublic])
async def list_movies(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """Show the details of all movies."""
    movies = session.exec(select(Movie).offset(offset).limit(limit)).all()
    return movies


@app.post("/v1/movies", response_model=MoviePublic)
async def create_movie(*, session: Session = Depends(get_session), movie: MovieCreate):
    """Create a new movie."""
    db_movie = Movie.model_validate(movie)
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return db_movie


@app.get("/v1/movies/{movie_id}", response_model=MoviePublic)
async def show_movie(
    *, session: Session = Depends(get_session), movie_id: int = Path(..., ge=1)
):
    """Show the details of a specific movie."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found"
        )
    return movie


@app.patch("/v1/movies/{movie_id}", response_model=MoviePublic)
async def update_movie(
    *,
    session: Session = Depends(get_session),
    movie_id: int = Path(..., ge=1),
    movie: MovieUpdate,
):
    """Update the details of a specific movie."""
    db_movie = session.get(Movie, movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found"
        )
    movie_data = movie.model_dump(exclude_unset=True)
    for key, value in movie_data.items():
        setattr(db_movie, key, value)
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return db_movie


@app.delete("/v1/movies/{movie_id}")
async def delete_movie(
    *,
    session: Session = Depends(get_session),
    movie_id: int = Path(ge=1),
):
    """Delete a specific movie."""
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found"
        )
    session.delete(movie)
    session.commit()
    return {"ok": True}
