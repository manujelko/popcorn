import asyncio
import time
from collections import defaultdict, deque

from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_calls: int = 2, period: int = 1) -> None:
        super().__init__(app)
        self.max_calls = max_calls
        self.period = period
        self.rate_limiters: dict[str, deque[float]] = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        async with self.lock:
            access_times = self.rate_limiters[client_ip]

            while access_times and access_times[0] + self.period < current_time:
                access_times.popleft()

            if len(access_times) >= self.max_calls:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Too Many Requests"},
                )

            access_times.append(current_time)

        try:
            response = await call_next(request)
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except Exception:
            return JSONResponse(
                status_code=500, content={"detail": "Internal Server Error"}
            )
        return response
