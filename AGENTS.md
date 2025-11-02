# Repository Guidelines

## Project Structure & Module Organization
- Backend in `src/seedscape/`
  - App entry: `seedscape.main:app` (FastAPI)
  - API routers: `src/seedscape/api/`
  - Core logic/config: `src/seedscape/core/`
- Frontend static assets in `frontend/` (served by FastAPI)
- Data and runtime artifacts in `data/` (git-ignored)
- Utility scripts in `scripts/`; rules/config in `rules/`

## Build, Test, and Development Commands
- `make install` — install deps via Poetry (creates `.venv`) and run `npm install` in `frontend/` if present.
- `make dev` — run FastAPI with autoreload; watches `src` and `rules`.
- `make run` — run server without reload.
- `make test` — run ruff, mypy, and pytest (skips tools not installed).
- `make lint` — ruff (Python) + ESLint and Prettier check (frontend).
- `make format` — ruff format (Python) + Prettier write (frontend).
- `make clean` — remove caches and local artifacts.
- Config via `.env`/`.env.local` (e.g., `HOST=127.0.0.1`, `PORT=8000`, `APP_MODULE=seedscape.main:app`, `SEEDSCAPE_DATA_DIR=...`).

## Coding Style & Naming Conventions
- Python ≥ 3.10, 4-space indentation, UTF-8.
- Use type hints; prefer Pydantic models for API I/O.
- Naming: `snake_case` for modules/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Lint/format: `ruff` (and optional `black`), run `make format && make lint` before PRs.
- Keep modules small; place API routes under `seedscape/api/`, business logic in `seedscape/core/`.

## Testing Guidelines
- Framework: `pytest`. Place tests in `tests/` mirroring package paths.
- Name files `test_*.py`; use fixtures and type-checked boundaries.
- Aim for meaningful coverage on core generators, models, and routing.
- Run locally with `make test`.

## Commit & Pull Request Guidelines
- Commits: short imperative subject. Prefer Conventional Commit prefixes when sensible (e.g., `feat:`, `fix:`, `refactor:`). Group related changes.
- PRs: include a clear description, linked issues, and steps to verify (commands, screenshots for frontend changes). Keep diffs focused; update docs when behavior changes.

## Security & Configuration Tips
- Never commit secrets. Copy `.env.example` to `.env` and customize locally.
- Paths can be overridden: `SEEDSCAPE_DATA_DIR`, `SEEDSCAPE_FRONTEND_DIR`.
- Validate inputs at API boundaries; prefer Pydantic schemas over raw dicts.

## Campaign Biomes (Data‑Driven)
- Each campaign defines biomes and styles under `data/campaigns/<name>/`.
- `meta.json` must include:
  - `biomes`: list of biome keys (strings)
  - `biomes_css`: relative CSS filename (e.g., `biomes.css`)
- CSS is served at `/api/campaigns/<name>/assets/biomes.css` and is dynamically loaded by `frontend/main.js`.
- API helpers:
  - `GET /api/campaigns` → list campaigns
  - `GET /api/campaigns/{campaign}` → campaign meta
  - `GET /api/campaigns/{campaign}/biomes` → biome keys
  - `GET /api/campaigns/{campaign}/assets/biomes.css` → campaign CSS
- Fail‑fast: missing `biomes` or CSS triggers clear server‑side errors (500/404) with logs.
- Example: `data/campaigns/example/meta.json` and `data/campaigns/example/biomes.css`.
