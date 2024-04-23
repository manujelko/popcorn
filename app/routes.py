from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session, select

from . import version
from .dependencies import get_session
from .models import Movie, MovieCreate, MoviePublic, MovieUpdate

router = APIRouter(prefix="/v1")


@router.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    """Show routerlication information."""
    return {"status": "available", "version": version}


@router.get("/movies", response_model=list[MoviePublic])
async def list_movies(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """Show the details of all movies."""
    movies = session.exec(select(Movie).offset(offset).limit(limit)).all()
    return movies


@router.post("/movies", response_model=MoviePublic)
async def create_movie(*, session: Session = Depends(get_session), movie: MovieCreate):
    """Create a new movie."""
    db_movie = Movie.model_validate(movie)
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return db_movie


@router.get("/movies/{movie_id}", response_model=MoviePublic)
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


@router.patch("/movies/{movie_id}", response_model=MoviePublic)
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


@router.delete("/movies/{movie_id}")
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
