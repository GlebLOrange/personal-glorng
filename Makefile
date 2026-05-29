.PHONY: dev dev-lite dev-worker dev-bot dev-full prod test lint migrate seed seed-multicooker-recipes down logs bot-logs

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

migrate:
	docker compose exec server alembic upgrade head

seed:
	docker compose exec server python -m app.db.seed

seed-multicooker-recipes:
	docker compose exec server python -m app.db.seed_multicooker_recipes
