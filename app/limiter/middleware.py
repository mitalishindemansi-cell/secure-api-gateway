import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.limiter.redis_client import get_redis
from app.limiter.token_bucket import TokenBucketLimiter


logger = logging.getLogger(__name__)
settings = get_settings()

EXEMPT_PATHS = {"/health", "/docs", "/openapi.json"}


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, limiter: TokenBucketLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):

        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        client_ip = self.get_client_ip(request)

        allowed, remaining, retry_after = self.limiter.check(client_ip)

        if not allowed:
            logger.warning(
                "Rate limit exceeded for client %s",
                client_ip,
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "retry_after_seconds": round(retry_after, 2),
                },
                headers={
                    "Retry-After": str(max(1, round(retry_after))),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)

        response.headers["X-RateLimit-Remaining"] = str(
            max(0, int(remaining))
        )

        return response

    @staticmethod
    def get_client_ip(request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"


def build_rate_limit_middleware() -> TokenBucketLimiter:
    return TokenBucketLimiter(
        redis_client=get_redis(),
        capacity=settings.RATE_LIMIT_TOKENS,
        window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    )