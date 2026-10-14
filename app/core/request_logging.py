import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time_ms = (time.perf_counter() - start_time) * 1000

        forwarded = request.headers.get("x-forwarded-for")

        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        logger.info(
            "request completed | ip=%s | method=%s | path=%s | status=%s | response_time_ms=%.2f",
            client_ip,
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
        )

        return response