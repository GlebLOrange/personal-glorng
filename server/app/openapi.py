"""OpenAPI schema customization for dev Swagger UI."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "auth",
        "description": "Registration, login, tokens, and session cookies.",
    },
    {
        "name": "expenses",
        "description": "Monthly expense ledger, categories, rates, and CSV export.",
    },
    {
        "name": "tasks",
        "description": "Todobot task admin, intakes, and calendar sync queue.",
    },
    {"name": "recipes", "description": "Personal recipe book CRUD."},
    {"name": "email", "description": "Send and preview styled outbound emails."},
    {"name": "file-share", "description": "Upload and manage temporary shared files."},
    {"name": "url-shortener", "description": "Create and manage short redirect links."},
    {"name": "calculator", "description": "Server-side arithmetic evaluation."},
    {
        "name": "vid-download",
        "description": "YouTube video metadata and download helpers.",
    },
    {"name": "ai-chat", "description": "Grounded personal search chat for admin."},
    {"name": "search", "description": "Public portfolio keyword search and AI chat."},
    {"name": "audit", "description": "Security and domain audit event log."},
    {"name": "app-logs", "description": "Persisted structured application logs."},
    {"name": "feedback", "description": "Visitor feedback inbox (admin read)."},
    {
        "name": "time-date-weather-location",
        "description": "Weather lookup, clocks bar config, and saved locations.",
    },
    {"name": "platform", "description": "Admin service catalog and capabilities."},
    {"name": "resume", "description": "Public portfolio resume content."},
    {"name": "donations", "description": "Public donation configuration."},
    {"name": "spotify", "description": "Public now-playing widget data."},
    {"name": "callbacks", "description": "OAuth and third-party callback handlers."},
    {"name": "github", "description": "GitHub OAuth linking for admin."},
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

**Admin permissions**
- Tool routes require platform capabilities: `slug:read` or `slug:write`
  (e.g. `expenses:read`).
- Unauthenticated public routes are tagged separately.
"""


def requires_capability(slug: str, capability: str) -> str:
    """OpenAPI description fragment for capability-gated routes."""
    return f"Requires permission `{slug}:{capability}`."


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
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
