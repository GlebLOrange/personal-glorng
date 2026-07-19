.PHONY: dev dev-lite dev-lite-client docs-dev docs-build docs-generate adr-new
.PHONY: dev-ultra-lite-infra dev-ultra-lite-server dev-search dev-postgres dev-worker dev-bot dev-full
.PHONY: prod prod-cloudflare test lint lint-check check check-symlinks migrate db-init db-init-ultra-lite db-reset db-revision db-current db-downgrade db-check seed seed-ultra-lite seed-multicooker-recipes reindex-search backup backup-install db-pull-prod down logs bot-logs

msg ?=
TITLE ?=
CHECK_DB ?= 1
COMPOSE_ULTRA = docker compose -f docker-compose.yml -f docker-compose.ultra-lite.yml
COMPOSE_CACHE = -f docker-compose.cache.yml
COMPOSE_BASE_CACHE = -f docker-compose.yml $(COMPOSE_CACHE)
DOCKER_BUILD = DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1
ULTRA_LITE_ENV = GLORNG_ENV_FILE=$(CURDIR)/.env UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv CELERY_TASK_ALWAYS_EAGER=true MEDIA_DIR=$(CURDIR)/server/media

dev:
	$(DOCKER_BUILD) docker compose $(COMPOSE_BASE_CACHE) up --build

dev-lite:
	@echo ""
	@echo "dev-lite: mongodb, redis, API, nginx are starting."
	@echo "  http://localhost needs host Vite — run in another terminal: make dev-lite-client"
	@echo "  Or use http://localhost:3000 after Vite is up (API docs: http://127.0.0.1:8000/api/docs)"
	@echo ""
	$(DOCKER_BUILD) docker compose -f docker-compose.yml -f docker-compose.lite.yml $(COMPOSE_CACHE) up --build mongodb redis server nginx

dev-lite-client:
	cd client && npm run dev

dev-ultra-lite-infra:
	$(DOCKER_BUILD) $(COMPOSE_ULTRA) $(COMPOSE_CACHE) up -d mongodb redis
	$(DOCKER_BUILD) $(COMPOSE_ULTRA) $(COMPOSE_CACHE) run --rm migrate

dev-ultra-lite-server:
	cd server && $(ULTRA_LITE_ENV) uv sync --frozen && $(ULTRA_LITE_ENV) uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app --forwarded-allow-ips=127.0.0.1

dev-search:
	$(DOCKER_BUILD) docker compose -f docker-compose.yml -f docker-compose.lite.yml -f docker-compose.search.yml $(COMPOSE_CACHE) --profile search up --build mongodb redis elasticsearch server

dev-postgres:
	$(DOCKER_BUILD) docker compose -f docker-compose.yml -f docker-compose.lite.yml $(COMPOSE_CACHE) --profile postgres up --build mongodb redis db server

dev-worker:
	$(DOCKER_BUILD) docker compose $(COMPOSE_BASE_CACHE) --profile worker up --build

dev-bot:
	$(DOCKER_BUILD) docker compose $(COMPOSE_BASE_CACHE) --profile bot up --build

dev-full:
	$(DOCKER_BUILD) docker compose $(COMPOSE_BASE_CACHE) --profile worker --profile bot up --build

prod:
	$(DOCKER_BUILD) docker compose -f docker-compose.prod.yml $(COMPOSE_CACHE) up --build -d

prod-cloudflare:
	$(DOCKER_BUILD) docker compose -f docker-compose.prod.yml -f docker-compose.cloudflare.yml $(COMPOSE_CACHE) up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

bot-logs:
	docker compose --profile bot logs -f todobot

test:
	docker compose exec server pytest -v

lint:
	docker compose exec server ruff check --fix . && docker compose exec server ruff format .

lint-check:
	docker compose exec server ruff check . && docker compose exec server ruff format --check .

check-symlinks:
	bash scripts/check_symlinks.sh

check: lint-check test
ifeq ($(CHECK_DB),1)
	$(MAKE) db-check
endif
	cd client && npm run lint && npm run format:check && npm run test && npm run build:check

db-init:
	$(DOCKER_BUILD) docker compose $(COMPOSE_BASE_CACHE) run --rm --build migrate

db-init-ultra-lite:
	$(COMPOSE_ULTRA) run --rm migrate

migrate: db-init

db-reset:
	docker compose down -v
	docker compose up -d db
	$(DOCKER_BUILD) docker compose $(COMPOSE_BASE_CACHE) run --rm --build migrate

db-revision:
	@test -n "$(msg)" || (echo "Usage: make db-revision msg='description'" && exit 1)
	docker compose exec server alembic revision --autogenerate -m "$(msg)"

db-current:
	docker compose exec server alembic current

db-downgrade:
	docker compose exec server alembic downgrade -1

db-check:
	docker compose exec server alembic check

seed:
	docker compose exec server python -m app.db.seed

seed-ultra-lite:
	cd server && $(ULTRA_LITE_ENV) uv run python -m app.db.seed

seed-multicooker-recipes:
	docker compose exec server python -m app.db.seed_multicooker_recipes

seed-demo:
	docker compose exec server python -m app.db.seed_demo --count 50 --reset

seed-demo-add:
	docker compose exec server python -m app.db.seed_demo --count 50 --no-reset

reindex-search:
	docker compose exec server python scripts/reindex_search.py

backup:
	bash scripts/db_maintenance.sh

backup-install:
	bash scripts/install_backup_cron.sh

db-pull-prod:
	bash scripts/pull_prod_db.sh

docs-generate:
	cd server && GLORNG_ENV_FILE=$(CURDIR)/server/tests/.env.test \
		UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv \
		uv run python ../scripts/generate_docs.py

docs-dev: docs-generate
	cd docs && npm run dev

docs-build: docs-generate
	cd docs && npm run build

adr-new:
	TITLE="$(TITLE)" bash scripts/adr-new.sh
