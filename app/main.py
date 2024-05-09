from contextlib import asynccontextmanager

from fastapi import FastAPI

# from .internal.database import create_db_and_tables
from .middlewares import RateLimiterMiddleware
from .routers import v1


@asynccontextmanager
async def lifespan(_: FastAPI):
    # await create_db_and_tables()
    yield


def create_app(enable_rate_limiter: bool = True) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(v1.router)

    if enable_rate_limiter:
        app.add_middleware(RateLimiterMiddleware, max_calls=2, period=1)

    return app


app = create_app(enable_rate_limiter=True)
