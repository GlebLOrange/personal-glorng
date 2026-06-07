FROM python:3.14.5-alpine3.23 AS base

WORKDIR /app

FROM base AS builder

RUN apk add --no-cache build-base

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

FROM base AS dev

RUN apk add --no-cache ffmpeg build-base bash libstdc++ wget

COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

COPY docker-entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "app", "--forwarded-allow-ips", "127.0.0.1"]

FROM base AS production

RUN apk add --no-cache ffmpeg

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

COPY docker-entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/docker-entrypoint.sh /app/scripts/db_init.sh \
    && adduser -D -H appuser
USER appuser

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
