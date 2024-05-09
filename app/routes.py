import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from . import version
from .dependencies import get_current_active_user, get_session
from .env import ACCESS_TOKEN_EXPIRE_MINUTES, ENVIRONMENT
from .log import logger
from .models import (
    Movie,
    MovieCreate,
    MoviePublic,
    MovieUpdate,
    Token,
    User,
    UserPublic,
)
from .security import authenticate_user, create_access_token

router = APIRouter(prefix="/v1")


@router.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    """Show routerlication information."""
    await logger.adebug("This is a test log", hello="world")
    return {"status": "available", "version": version, "environment": ENVIRONMENT}


@router.get("/movies", response_model=list[MoviePublic])
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


@router.post("/movies", response_model=MoviePublic)
async def create_movie(
    *, session: Annotated[AsyncSession, Depends(get_session)], movie: MovieCreate
):
    """Create a new movie."""
    db_movie = Movie.model_validate(movie)
    session.add(db_movie)
    await session.commit()
    await session.refresh(db_movie)
    return db_movie


@router.get("/movies/{movie_id}", response_model=MoviePublic)
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


@router.patch("/movies/{movie_id}", response_model=MoviePublic)
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


@router.delete("/movies/{movie_id}")
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


@router.post("/token")
async def login_for_access_token(
    *,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Token:
    user = await authenticate_user(
        form_data.username, form_data.password, session=session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
