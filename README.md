# IIS Project

Web application built with React (Vite), FastAPI, and PostgreSQL — fully containerized with Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Docker Compose v2
- Git

## Quick start

```bash
# 1. Clone the repo
git clone <repo-url>
cd IIS-Project

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env if needed (defaults work for local dev)

# 3. Start all services
docker compose up --build
```

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:5173        |
| API      | http://localhost:8000        |
| API docs | http://localhost:8000/docs   |
| Postgres | localhost:5432               |

## Project structure

```
├── backend/          FastAPI app (Python 3.12, async SQLAlchemy)
│   ├── alembic/      Database migrations
│   ├── main.py       App entry point
│   └── database.py   DB session / Base
├── frontend/         React app (Vite 5)
│   └── src/
├── docker-compose.yml
└── .env.example      Required environment variables
```

## Development

Hot reload is enabled for both services out of the box:
- **Frontend**: Vite HMR on http://localhost:5173
- **Backend**: uvicorn `--reload` watches `/app`

### Running database migrations

```bash
# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec backend alembic upgrade head
```

### Environment variables

| Variable          | Default      | Description            |
|-------------------|--------------|------------------------|
| POSTGRES_USER     | appuser      | DB username            |
| POSTGRES_PASSWORD | apppassword  | DB password            |
| POSTGRES_DB       | appdb        | DB name                |
| POSTGRES_HOST     | db           | DB host (service name) |
| POSTGRES_PORT     | 5432         | DB port                |
