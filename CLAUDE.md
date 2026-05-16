# IIS Project

React (Vite 5) + FastAPI + PostgreSQL 16, all running in Docker Compose.

## Start dev environment

```bash
docker compose up --build
```

## Key URLs

- Frontend: http://localhost:5173
- API + docs: http://localhost:8000/docs
- Postgres: localhost:5432

## Backend

- Async SQLAlchemy + asyncpg for all DB access
- Add models in `backend/` by subclassing `Base` from `database.py`
- Migrations: `docker compose exec backend alembic revision --autogenerate -m "desc"` then `alembic upgrade head`

## Frontend

- Vite proxies `/api/*` → `http://backend:8000` (strips `/api` prefix)
- Entry: `frontend/src/App.jsx`

## Environment variables

Defined in `.env` (gitignored). Copy `.env.example` to get started.
