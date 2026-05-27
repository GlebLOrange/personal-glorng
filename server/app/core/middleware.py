"""Request-ID middleware for structured logging correlation."""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import logger


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id

        logger.info(
            "Request started",
            context={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
            },
        )

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Request completed",
            context={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "status": response.status_code,
            },
        )

        return response
