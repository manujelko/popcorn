from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.dependencies import get_session
from app.models.movies import Movie, MovieCreate, MoviePublic, MovieUpdate

router = APIRouter(prefix="/movies")


@router.get("", response_model=list[MoviePublic])
async def list_movies(
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """Show the details of all movies."""
    result = await session.exec(select(Movie).offset(offset).limit(limit))
    movies = result.all()
    return movies


@router.post("", response_model=MoviePublic)
async def create_movie(
    *, session: Annotated[AsyncSession, Depends(get_session)], movie: MovieCreate
):
    """Create a new movie."""
    db_movie = Movie.model_validate(movie)
    session.add(db_movie)
    await session.commit()
    await session.refresh(db_movie)
    return db_movie


@router.get("/{movie_id}", response_model=MoviePublic)
async def show_movie(
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
    movie_id: int = Path(..., ge=1),
):
    """Show the details of a specific movie."""
    movie = await session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie Not Found"
        )
    return movie


@router.patch("/{movie_id}", response_model=MoviePublic)
async def update_movie(
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
    movie_id: int = Path(..., ge=1),
    movie: MovieUpdate,
):
    """Update the details of a specific movie."""
    db_movie = await session.get(Movie, movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie Not Found"
        )
    movie_data = movie.model_dump(exclude_unset=True)
    for key, value in movie_data.items():
        setattr(db_movie, key, value)
    session.add(db_movie)
    await session.commit()
    await session.refresh(db_movie)
    return db_movie


@router.delete("/{movie_id}")
async def delete_movie(
    *,
    session: Annotated[AsyncSession, Depends(get_session)],
    movie_id: int = Path(ge=1),
):
    """Delete a specific movie."""
    movie = await session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Movie Not Found"
        )
    await session.delete(movie)
    await session.commit()
    return {"ok": True}
