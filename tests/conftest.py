from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from app.dependencies import get_session
from app.main import create_app


@pytest.fixture()
def anyio_backend():
    return "asyncio"


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
async def app(session: AsyncSession) -> AsyncGenerator[FastAPI, None]:
    def get_session_override():
        return session

    app_ = create_app(enable_rate_limiter=False)
    app_.dependency_overrides[get_session] = get_session_override
    yield app_
    app_.dependency_overrides.clear()


@pytest.fixture()
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),  # type: ignore
        base_url="http://test",
    ) as client:
        yield client
