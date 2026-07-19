# ADR 0002: OpenAPI interactive docs only in development

- **Status:** Accepted
- **Date:** 2026-07-19

## Context

FastAPI can expose Swagger UI, ReDoc, and `/openapi.json` in every environment. Shipping interactive Try-it-out against production increases attack surface and encourages credential use in the browser against live data.

## Decision

Mount `/api/docs`, `/api/redoc`, and `/api/openapi.json` **only when `APP_ENV=development`**. For static handbook consumers, export OpenAPI via `make docs-generate` into `docs/generated/` (and `docs/public/openapi.json` for download).

## Consequences

- Production and staging do not serve Swagger.
- Postman and CI use the committed/generated schema or a local dev API.
- Capability and auth narrative stay in curated handbook pages alongside the generated endpoint table.
