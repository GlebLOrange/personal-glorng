-- Runs only on first Postgres volume init (docker-entrypoint-initdb.d).
-- Existing databases get the same extensions via Alembic revision c9d0e1f2a3b4.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
