"""
Request/Response Logging Middleware.
Log mọi request đến server với thời gian xử lý.
"""

import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("api.access") 


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log format:
      ← POST /api/v1/students 201 (52ms)
      ← GET  /api/v1/students/999 404 (12ms)
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.perf_counter() # Bắt đầu đếm thời gian

        # Xử lý request
        response = await call_next(request)

        # Tính thời gian
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Chọn log level theo status code
        status = response.status_code
        if status >= 500:
            log_fn = logger.error
        elif status >= 400:
            log_fn = logger.warning
        else:
            log_fn = logger.info

        log_fn(
            "%-6s %s %s (%dms)",
            request.method,
            request.url.path,
            status,
            elapsed_ms,
        )

        return response
