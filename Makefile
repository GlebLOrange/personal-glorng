.PHONY: dev prod test lint migrate seed seed-multicooker-recipes down logs bot-logs

dev:
	docker compose up --build

prod:
	docker compose -f docker-compose.prod.yml up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

bot-logs:
	docker compose logs -f todobot

test:
	docker compose exec server pytest -v

lint:
	docker compose exec server ruff check --fix . && docker compose exec server ruff format .

migrate:
	docker compose exec server alembic upgrade head

seed:
	docker compose exec server python -m app.seed

seed-multicooker-recipes:
	docker compose exec server python -m app.seed_multicooker_recipes
