# ADR 0001: MongoDB primary with optional PostgreSQL

- **Status:** Accepted
- **Date:** 2026-07-19

## Context

The platform needs a primary document store for portfolio and tool data, plus optional full-text search and audit secondary storage. Not every deploy wants Postgres or Elasticsearch.

## Decision

Use **MongoDB as the primary database**. PostgreSQL is optional (`--profile postgres`) for secondary FTS search and audit dual-write. Elasticsearch is optional for search (`make dev-search`). Feature flags and empty URLs keep lite mode free of those dependencies.

## Consequences

- Lite and ultra-lite workflows stay simple (Mongo + Redis).
- Search/audit features must tolerate missing Postgres/ES.
- Schema and migration stories differ by store; ops docs cover each path.
