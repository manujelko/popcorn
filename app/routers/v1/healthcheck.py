from fastapi import APIRouter

from app import version
from app.internal.env import ENVIRONMENT
from app.internal.log import logger

router = APIRouter(prefix="/healthcheck")


@router.get("")
async def healthcheck() -> dict[str, str]:
    """Show routerlication information."""
    await logger.adebug("This is a test log", hello="world")
    return {"status": "available", "version": version, "environment": ENVIRONMENT}
