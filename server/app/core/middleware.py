"""Request-ID middleware for structured logging correlation."""

import json
import time
import uuid
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.csrf import csrf_origin_rejected
from app.core.logging import logger
from app.core.request_context import request_id_var, user_id_var
from app.core.security import access_token_from_request, user_id_from_access_token
from app.settings import get_settings

_BODY_LOG_MAX_CHARS = 2048
_SENSITIVE_BODY_KEYS = frozenset(
    {"password", "token", "authorization", "secret", "cookie", "access_token"},
)


def _optional_user_id(request: Request) -> int | None:
    raw_token = access_token_from_request(request)
    if not raw_token:
        return None
    return user_id_from_access_token(raw_token)


def _sanitize_body_for_log(raw: bytes) -> str | None:
    if not raw:
        return None
    text = raw.decode("utf-8", errors="replace")
    if len(text) > _BODY_LOG_MAX_CHARS:
        text = text[: _BODY_LOG_MAX_CHARS - 3] + "..."
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text
    if isinstance(payload, dict):
        return json.dumps(_redact_body_dict(payload), default=str)
    return text


def _redact_body_dict(payload: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if key.lower() in _SENSITIVE_BODY_KEYS or any(
            marker in key.lower() for marker in ("password", "token", "secret")
        ):
            redacted[key] = "[REDACTED]"
        elif isinstance(value, dict):
            redacted[key] = _redact_body_dict(value)
        else:
            redacted[key] = value
    return redacted


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
            body_bytes = await request.body()

            async def receive() -> dict[str, Any]:
                return {"type": "http.request", "body": body_bytes, "more_body": False}

            request = Request(request.scope, receive)
            body_log = _sanitize_body_for_log(body_bytes)

        if settings.LOG_REQUESTS:
            started_context = dict(log_ctx)
            if body_log is not None:
                started_context["body"] = body_log
            logger.info("Request started", context=started_context)

        # #region agent log
        if request.url.path == "/api/resume/pdf":
            import json

            with open(
                "/Users/glorange/projects/portfolio-glorng/.cursor/debug-27ee16.log",
                "a",
                encoding="utf-8",
            ) as _f:
                _f.write(
                    json.dumps(
                        {
                            "sessionId": "27ee16",
                            "location": "middleware.py:dispatch:resume-pdf",
                            "message": "Resume PDF request reached API",
                            "data": {
                                "client_host": request.client.host if request.client else None,
                            },
                            "timestamp": int(time.time() * 1000),
                            "hypothesisId": "H1",
                        }
                    )
                    + "\n"
                )
        # #endregion

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

        # #region agent log
        if request.url.path == "/api/resume/pdf":
            import json

            with open(
                "/Users/glorange/projects/portfolio-glorng/.cursor/debug-27ee16.log",
                "a",
                encoding="utf-8",
            ) as _f:
                _f.write(
                    json.dumps(
                        {
                            "sessionId": "27ee16",
                            "location": "middleware.py:dispatch:resume-pdf-done",
                            "message": "Resume PDF request completed",
                            "data": {
                                "status": response.status_code,
                                "duration_ms": completed_ctx["duration_ms"],
                            },
                            "timestamp": int(time.time() * 1000),
                            "hypothesisId": "H2",
                        }
                    )
                    + "\n"
                )
        # #endregion

        return response
