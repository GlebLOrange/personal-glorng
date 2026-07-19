"""OpenAPI schema customization for dev Swagger UI."""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.schemas.common import ErrorResponse

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "auth",
        "description": "Registration, login, tokens, and session cookies.",
    },
    {
        "name": "admin",
        "description": "Platform admin user management and stats.",
    },
    {
        "name": "health",
        "description": "Liveness and readiness probes.",
    },
    {
        "name": "expenses",
        "description": "Monthly expense ledger, categories, rates, and CSV export.",
    },
    {
        "name": "expense-calculator",
        "description": "Public expense calculator helpers and saved calculator state.",
    },
    {
        "name": "tasks",
        "description": "Todobot task admin, intakes, and calendar sync queue.",
    },
    {"name": "recipes", "description": "Personal recipe book CRUD."},
    {"name": "news", "description": "Curated news digest and publishing workflow."},
    {"name": "email", "description": "Send and preview styled outbound emails."},
    {"name": "file-share", "description": "Upload and manage temporary shared files."},
    {"name": "url-shortener", "description": "Create and manage short redirect links."},
    {"name": "calculator", "description": "Server-side arithmetic evaluation."},
    {
        "name": "password-generator",
        "description": "Public random password generation.",
    },
    {
        "name": "vid-download",
        "description": "YouTube video metadata and download helpers.",
    },
    {"name": "ai-chat", "description": "Superuser-only plain LLM chat."},
    {
        "name": "data-extract",
        "description": "Upload, stage, and promote tabular data extracts.",
    },
    {"name": "search", "description": "Public portfolio keyword search."},
    {"name": "audit", "description": "Security and domain audit event log."},
    {"name": "app-logs", "description": "Persisted structured application logs."},
    {"name": "feedback", "description": "Visitor feedback inbox (admin read)."},
    {
        "name": "weather",
        "description": "Weather lookup, saved locations, and local time.",
    },
    {"name": "platform", "description": "Admin service catalog and capabilities."},
    {"name": "resume", "description": "Public portfolio resume content."},
    {"name": "donations", "description": "Public donation configuration."},
    {"name": "spotify", "description": "Public now-playing widget data."},
    {"name": "callbacks", "description": "OAuth and third-party callback handlers."},
    {"name": "github", "description": "GitHub OAuth linking for admin."},
    {
        "name": "webhooks",
        "description": "HMAC-signed inbound automation webhooks.",
    },
    {"name": "seo", "description": "Sitemap and robots endpoints."},
    {"name": "amp", "description": "AMP HTML portfolio mirror."},
]

API_DESCRIPTION = """
Gleb.Y HTTP API. All JSON routes are under `/api`.

**Swagger (development only):** `/api/docs` when `APP_ENV=development`.

**Authentication**
- Browser SPA: HttpOnly `access_token` / `refresh_token` cookies after
  `POST /api/auth/login`.
- Swagger Try-it-out: use **Authorize** with `Bearer <access_token>` from the
  login response.
- Click Authorize once; Bearer is attached to protected operations automatically.

**Errors**
- Application errors use `{"detail": "<string>"}` (`ErrorResponse`).
- Validation failures (422) use the same string `detail` envelope.

**Admin permissions**
- Tool routes require platform capabilities: `slug:read` or `slug:write`
  (e.g. `expenses:read`).
- Unauthenticated public routes are tagged separately.
"""

_ERROR_RESPONSE_REF = {"$ref": "#/components/schemas/ErrorResponse"}

_COMMON_ERROR_RESPONSES: dict[str, dict[str, Any]] = {
    "401": {
        "description": "Not authenticated",
        "content": {"application/json": {"schema": _ERROR_RESPONSE_REF}},
    },
    "403": {
        "description": "Forbidden",
        "content": {"application/json": {"schema": _ERROR_RESPONSE_REF}},
    },
    "404": {
        "description": "Not found",
        "content": {"application/json": {"schema": _ERROR_RESPONSE_REF}},
    },
    "422": {
        "description": "Validation error",
        "content": {"application/json": {"schema": _ERROR_RESPONSE_REF}},
    },
    "500": {
        "description": "Internal server error",
        "content": {"application/json": {"schema": _ERROR_RESPONSE_REF}},
    },
}

# Tags with mostly authenticated routes. Public endpoints in these tags
# still work without a token; Swagger may prompt Authorize for Try-it-out.
_PROTECTED_TAGS = frozenset(
    {
        "admin",
        "ai-chat",
        "app-logs",
        "audit",
        "data-extract",
        "email",
        "expenses",
        "file-share",
        "github",
        "platform",
        "tasks",
    }
)


def requires_capability(slug: str, capability: str) -> str:
    """OpenAPI description fragment for capability-gated routes."""
    return f"Requires permission `{slug}:{capability}`."


def _inject_error_responses(schema: dict[str, Any]) -> None:
    """Document ErrorResponse on common 4xx/5xx for all operations."""
    for path_item in schema.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method not in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "head",
                "options",
            }:
                continue
            if not isinstance(operation, dict):
                continue
            responses = operation.setdefault("responses", {})
            for code, payload in _COMMON_ERROR_RESPONSES.items():
                responses.setdefault(code, payload)


def _bind_bearer_security(schema: dict[str, Any]) -> None:
    """Attach HTTPBearer when an operation documents a required capability."""
    for path_item in schema.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            if not isinstance(operation, dict):
                continue
            description = operation.get("description") or ""
            tags = set(operation.get("tags") or [])
            if "Requires permission" in description or tags & _PROTECTED_TAGS:
                operation.setdefault("security", [{"HTTPBearer": []}])


def configure_openapi(app: FastAPI) -> None:
    """Attach enriched OpenAPI metadata and Bearer security scheme."""

    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=API_DESCRIPTION,
            routes=app.routes,
            tags=OPENAPI_TAGS,
        )
        components = schema.setdefault("components", {})
        security_schemes = components.setdefault("securitySchemes", {})
        security_schemes.setdefault(
            "HTTPBearer",
            {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Access token from POST /api/auth/login",
            },
        )
        schemas = components.setdefault("schemas", {})
        schemas.setdefault("ErrorResponse", ErrorResponse.model_json_schema())
        _inject_error_responses(schema)
        _bind_bearer_security(schema)
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
