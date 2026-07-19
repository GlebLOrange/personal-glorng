"""Request-ID middleware for structured logging correlation."""

import json
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.csrf import csrf_origin_rejected
from app.core.logging import logger
from app.core.request_context import request_id_var, user_id_var
from app.core.security import access_token_from_request, user_id_from_access_token
from app.settings import get_settings

_BODY_LOG_MAX_CHARS = 2048
_BODY_LOG_MAX_BYTES = 64 * 1024
_SKIP_BODY_LOG_CONTENT_TYPES = (
    "multipart/form-data",
    "application/octet-stream",
    "application/pdf",
    "image/",
    "audio/",
    "video/",
)
_SENSITIVE_BODY_KEYS = frozenset(
    {
        "password",
        "token",
        "authorization",
        "secret",
        "cookie",
        "access_token",
        "api_key",
        "apikey",
    },
)


def _should_skip_body_log(content_type: str | None) -> bool:
    if not content_type:
        return False
    lowered = content_type.lower()
    return any(marker in lowered for marker in _SKIP_BODY_LOG_CONTENT_TYPES)


async def _read_body_for_log(request: Request) -> bytes | None:
    """Read a bounded body for logging, or None when logging should be skipped."""
    content_type = request.headers.get("content-type")
    if _should_skip_body_log(content_type):
        return None

    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > _BODY_LOG_MAX_BYTES:
                return None
        except ValueError:
            return None

    body_bytes = await request.body()
    if len(body_bytes) > _BODY_LOG_MAX_BYTES:
        return None
    return body_bytes


def _optional_user_id(request: Request) -> int | None:
    raw_token = access_token_from_request(request)
    if not raw_token:
        return None
    return user_id_from_access_token(raw_token)


def _sanitize_body_for_log(
    raw: bytes,
    *,
    content_type: str | None = None,
) -> str | None:
    if not raw:
        return None
    text = raw.decode("utf-8", errors="replace")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return (
            f"[non-json request body omitted: {len(raw)} bytes, "
            f"content_type={content_type or 'unknown'}]"
        )
    sanitized = json.dumps(_redact_body_value(payload), default=str)
    if len(sanitized) > _BODY_LOG_MAX_CHARS:
        return sanitized[: _BODY_LOG_MAX_CHARS - 3] + "..."
    return sanitized


def _redact_body_dict(payload: dict[str, object]) -> dict[str, object]:
    redacted: dict[str, object] = {}
    for key, value in payload.items():
        if key.lower() in _SENSITIVE_BODY_KEYS or any(
            marker in key.lower()
            for marker in ("password", "token", "secret", "api_key", "apikey")
        ):
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = _redact_body_value(value)
    return redacted


def _redact_body_value(value: object) -> object:
    if isinstance(value, dict):
        return _redact_body_dict(value)
    if isinstance(value, list):
        return [_redact_body_value(item) for item in value]
    return value


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        settings = get_settings()
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id
        user_id = _optional_user_id(request)
        started_at = time.perf_counter()

        req_token = request_id_var.set(request_id)
        user_token = user_id_var.set(user_id)

        log_ctx: dict[str, str | int] = {
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
        }
        if user_id is not None:
            log_ctx["user_id"] = user_id

        body_log: str | None = None
        if settings.LOG_REQUEST_BODIES and request.method in {"POST", "PUT", "PATCH"}:
            body_bytes = await _read_body_for_log(request)
            if body_bytes is not None:

                async def receive() -> dict[str, object]:
                    return {
                        "type": "http.request",
                        "body": body_bytes,
                        "more_body": False,
                    }

                request = Request(request.scope, receive)
                body_log = _sanitize_body_for_log(
                    body_bytes,
                    content_type=request.headers.get("content-type"),
                )

        if settings.LOG_REQUESTS:
            started_context = dict(log_ctx)
            if body_log is not None:
                started_context["body"] = body_log
            logger.info("Request started", context=started_context)

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

        completed_ctx: dict[str, str | int | float] = {
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "status": response.status_code,
            "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
        }
        if user_id is not None:
            completed_ctx["user_id"] = user_id

        if settings.LOG_REQUESTS:
            logger.info("Request completed", context=completed_ctx)

        return response
