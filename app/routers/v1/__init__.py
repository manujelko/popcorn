from fastapi import APIRouter

from . import healthcheck, movies, tokens, users

router = APIRouter(prefix="/v1")

for sub_router in [healthcheck.router, movies.router, tokens.router, users.router]:
    router.include_router(sub_router)
