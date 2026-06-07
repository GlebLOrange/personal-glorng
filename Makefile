.PHONY: dev dev-lite dev-worker dev-bot dev-full prod test lint lint-check check check-symlinks migrate db-init db-reset db-revision db-current db-downgrade db-check seed seed-multicooker-recipes reindex-search backup backup-install db-pull-prod down logs bot-logs

msg ?=
CHECK_DB ?= 1

dev:
	docker compose up --build

dev-lite:
	docker compose -f docker-compose.yml -f docker-compose.lite.yml up --build db redis server

dev-worker:
	docker compose --profile worker up --build

dev-bot:
	docker compose --profile bot up --build

dev-full:
	docker compose --profile worker --profile bot up --build

prod:
	docker compose -f docker-compose.prod.yml up --build -d

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
	cd client && npm run lint && npm run format:check && npm run test && npm run build

db-init:
	docker compose run --rm --build migrate

migrate: db-init

db-reset:
	docker compose down -v
	docker compose up -d db
	docker compose run --rm --build migrate

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
