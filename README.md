# Financial Cashflow Recording & BI Reporting App

Monorepo for a centralized cashflow recording and BI dashboard application.

- `apps/web` — Next.js frontend (App Router)
- `apps/api` — FastAPI backend (repository pattern over Supabase, no ORM)
- `supabase/` — PostgreSQL migrations and seed data
- `deploy/` — Docker Compose, Nginx config, environment template
- `scripts/` — operational scripts (upload backup/restore)
- `docs/` — specification, ADRs, agent docs

See `CONTEXT.md` for the domain model and `AGENTS.md` for build rules.

## Prerequisites

- Node.js >= 22 (frontend)
- Python >= 3.11 (< 3.14) (backend)
- Docker + Docker Compose (full stack)
- A Supabase project with PostgreSQL and Auth enabled (manual — created by the maintainer)

## Backend (local)

All Python commands must run inside the project virtual environment at
`apps/api/.venv` (never the system Python).

```bash
cd apps/api
source .venv/Scripts/activate   # Windows Git Bash
# source .venv/bin/activate       # Linux/macOS
python -m pip install .           # install app + dependencies into the venv
ruff check .
mypy .
pytest
uvicorn app.main:app --reload
```

Health check: `http://localhost:8000/api/health` returns `{"status": "ok"}`.

## Frontend (local)

```bash
cd apps/web
npm install
npm run lint
npm run typecheck
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Full stack with Docker Compose

```bash
cd deploy
cp .env.example .env   # fill in real Supabase values
docker compose up --build
```

Nginx routes `/api/*` to FastAPI and `/*` to Next.js on port 80.

## Environment variables

See `deploy/.env.example` for the full list and placeholder values. Public
`NEXT_PUBLIC_*` variables are safe for the browser; all other variables are
backend-only and must never be exposed to the frontend.