from contextlib import asynccontextmanager

from fastapi import FastAPI

# from .database import create_db_and_tables
from .middleware import RateLimiterMiddleware
from .routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # await create_db_and_tables()
    yield


def create_app(enable_rate_limiter: bool = True) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    if enable_rate_limiter:
        app.add_middleware(RateLimiterMiddleware, max_calls=2, period=1)

    return app


app = create_app(enable_rate_limiter=True)
