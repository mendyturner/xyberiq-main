# XyberIQ Backend

Production-ready FastAPI backend scaffold for the XyberIQ compliance training platform.

## Features
- FastAPI application structured by domain (`app/api`, `app/core`, `app/db`, `app/schemas`, `app/services`, `app/jobs`, `app/utils`)
- Poetry-managed dependencies targeting Python 3.11+
- SQLAlchemy 2.x + Alembic migrations with UUID primary keys and tenant-aware mixins
- Redis + RQ integration scaffolding for background jobs
- Structlog-based JSON logging, health/version endpoints, and `.env`-driven configuration via `pydantic-settings`
- Developer tooling: Makefile, pytest, black, isort, ruff, pre-commit hooks
- Docker Compose with API, PostgreSQL, and Redis services

## Getting Started

1. **Install dependencies**

   ```bash
   poetry install
   ```

2. **Copy environment template**

   ```bash
   cp .env.example .env
   ```

   Update secrets such as `XYBERIQ_JWT_SECRET_KEY` before running in production.

3. **Run database migrations**

   ```bash
   make migrate
   ```

4. **Start the API**

   ```bash
   make run
   ```

   The service listens on http://localhost:8000 with an OpenAPI schema at `/docs`.

## Development

- Format and lint the codebase:

  ```bash
  make fmt
  make lint
  ```

- Run tests locally:

  ```bash
  make test
  ```

- Install pre-commit hooks:

  ```bash
  make precommit-install
  ```

## Docker Compose

Spin up PostgreSQL, Redis, and the API locally:

```bash
docker compose up --build
```

The API container runs `uvicorn` with live reload, mounting the project directory for rapid iteration.

## Next Steps

- Implement domain models, RBAC, and tenant-aware services.
- Configure Redis-backed JWT revocation and background job pipelines.
- Extend Alembic migrations and seeding scripts for baseline compliance data.
