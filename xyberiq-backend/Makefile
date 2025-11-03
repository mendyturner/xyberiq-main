.PHONY: run fmt lint test coverage migrate seed precommit-install worker

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	poetry run rq worker $(QUEUE)

fmt:
	poetry run black app tests
	poetry run isort app tests

lint:
	poetry run ruff check app tests
	poetry run black --check app tests
	poetry run isort --check-only app tests

test:
	poetry run pytest

coverage:
	poetry run pytest --cov=app --cov-report=term-missing

migrate:
	poetry run alembic upgrade head

seed:
	poetry run python -m app.scripts.seed

precommit-install:
	poetry run pre-commit install
