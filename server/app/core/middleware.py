"""Request-ID middleware for structured logging correlation."""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.csrf import csrf_origin_rejected
from app.core.logging import logger
from app.core.request_context import request_id_var, user_id_var
from app.core.security import decode_token


def _optional_user_id(request: Request) -> int | None:
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return None
    token = auth[7:].strip()
    if not token:
        return None
    try:
        payload = decode_token(token)
    except ValueError:
        return None
    if payload.get("type") != "access":
        return None
    sub = payload.get("sub")
    if not sub:
        return None
    try:
        return int(sub)
    except (ValueError, TypeError):
        return None


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id
        user_id = _optional_user_id(request)

        req_token = request_id_var.set(request_id)
        user_token = user_id_var.set(user_id)

        log_ctx: dict[str, str | int] = {
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
        }
        if user_id is not None:
            log_ctx["user_id"] = user_id

        logger.info("Request started", context=log_ctx)

        if csrf_origin_rejected(request):
            return JSONResponse(
                status_code=403,
                content={"detail": "Origin not allowed"},
                headers={"X-Request-ID": request_id},
            )

        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(req_token)
            user_id_var.reset(user_token)

        response.headers["X-Request-ID"] = request_id

        completed_ctx: dict[str, str | int] = {
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "status": response.status_code,
        }
        if user_id is not None:
            completed_ctx["user_id"] = user_id

        logger.info("Request completed", context=completed_ctx)

        return response
