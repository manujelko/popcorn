from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from app.dependencies import get_session
from app.main import create_app
from app.models import Movie

pytestmark = pytest.mark.anyio


@pytest.fixture()
async def session() -> AsyncGenerator[AsyncSession, None]:
    sqlite_url = "sqlite+aiosqlite://"
    engine = create_async_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture()
async def app(session: Session) -> AsyncGenerator[FastAPI, None]:
    def get_session_override():
        return session

    app_ = create_app(enable_rate_limiter=False)
    app_.dependency_overrides[get_session] = get_session_override
    yield app_
    app_.dependency_overrides.clear()


@pytest.fixture()
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


async def test_create_movie(client: AsyncClient) -> None:
    response = await client.post(
        "/v1/movies", json={"title": "Moana", "year": 2016, "runtime": 107}
    )
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == 1
    assert data["title"] == "Moana"
    assert data["year"] == 2016
    assert data["runtime"] == 107


async def test_create_movie_incomplete(client: AsyncClient) -> None:
    response = await client.post("/v1/movies", json={"title": "Moana"})
    assert response.status_code == 422


async def test_read_movies(session: AsyncSession, client: AsyncClient):
    movie_1 = Movie(title="Moana", year=2016, runtime=107)
    movie_2 = Movie(title="The Martian", year=2015, runtime=151)
    session.add(movie_1)
    session.add(movie_2)
    await session.commit()

    response = await client.get("/v1/movies")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 2
    assert data[0]["title"] == "Moana"
    assert data[0]["year"] == 2016
    assert data[0]["runtime"] == 107
    assert data[0]["id"] == movie_1.id
    assert data[1]["title"] == "The Martian"
    assert data[1]["year"] == 2015
    assert data[1]["runtime"] == 151
    assert data[1]["id"] == 2


async def test_read_movie(session: AsyncSession, client: AsyncClient):
    movie = Movie(title="Moana", year=2016, runtime=107)
    session.add(movie)
    await session.commit()
    await session.refresh(movie)

    response = await client.get(f"/v1/movies/{movie.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "Moana"
    assert data["year"] == 2016
    assert data["runtime"] == 107
    assert data["id"] == movie.id


async def test_update_movie(session: AsyncSession, client: AsyncClient) -> None:
    movie = Movie(title="Moana", year=2015, runtime=107)
    session.add(movie)
    await session.commit()
    await session.refresh(movie)

    response = await client.patch(f"/v1/movies/{movie.id}", json={"year": 2016})
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "Moana"
    assert data["year"] == 2016
    assert data["runtime"] == 107
    assert data["id"] == movie.id


async def test_delete_movie(session: AsyncSession, client: AsyncClient) -> None:
    movie = Movie(title="Moana", year=2015, runtime=107)
    session.add(movie)
    await session.commit()
    await session.refresh(movie)

    response = await client.delete(f"/v1/movies/{movie.id}")

    movie_in_db = await session.get(Movie, movie.id)

    assert response.status_code == 200
    assert movie_in_db is None
