# -------- SeedScape Makefile --------
SHELL := /bin/bash

# Load env from .env files (if present)
# This includes only lines with KEY=VALUE (ignores comments/empty/export).
ifneq (,$(wildcard .env))
include .env
export $(shell sed -n 's/^\s*\([^#][^=[:space:]]*\)\s*=.*/\1/p' .env)
endif
ifneq (,$(wildcard .env.local))
include .env.local
export $(shell sed -n 's/^\s*\([^#][^=[:space:]]*\)\s*=.*/\1/p' .env.local)
endif

# ---------------- Defaults (override in .env/.env.local) ----------------
# Server
HOST ?= 127.0.0.1
PORT ?= 8000
# Module path: keep generic; allow override via .env as APP_MODULE="seedscape.main:app"
APP_MODULE ?= seedscape.main:app
# Reload dirs to watch during dev; keep narrow to avoid .venv thrash
RELOAD_DIRS ?= src rules
# Reload excludes to prevent infinite loops
RELOAD_EXCLUDES ?= .venv .git node_modules dist build __pycache__ *.pyc
# Python version for venv (optional)
PY ?= python3

# Tools (can be swapped without changing README)
POETRY ?= poetry
UVICORN ?= uvicorn
PYTEST ?= pytest
MYPY ?= mypy
RUFF ?= ruff

# --------------- Helpers ---------------
define check_or_install_poetry
@if ! command -v $(POETRY) >/dev/null 2>&1; then \
  echo "Poetry not found. Installing..."; \
  curl -sSL https://install.python-poetry.org | $(PY) -; \
  echo "Please ensure Poetry is on your PATH (restart shell if needed)."; \
fi
endef

define run_if_exists
@if command -v $(1) >/dev/null 2>&1; then \
  echo "→ $(1)"; \
  $(POETRY) run $(1) $(2); \
else \
  echo "(!) Skipping: '$(1)' not installed."; \
fi
endef

# --------------- Targets ---------------
.PHONY: install install-poetry dev run test lint typecheck format clean export-req help

## Install dependencies (creates .venv) — stable entrypoint
install: install-poetry
	@echo "==> Installing dependencies"
	@$(POETRY) install

## Install Poetry if missing (auto-detect)
install-poetry:
	$(call check_or_install_poetry)

## Development server with autoreload and safe watch settings
dev:
	@echo "==> Starting development server (autoreload)"
	@set -e; \
	RELOAD_DIR_FLAGS=""; \
	for d in $(RELOAD_DIRS); do RELOAD_DIR_FLAGS="$$RELOAD_DIR_FLAGS --reload-dir $$d"; done; \
	EXCLUDE_FLAGS=""; \
	for x in $(RELOAD_EXCLUDES); do EXCLUDE_FLAGS="$$EXCLUDE_FLAGS --reload-exclude $$x"; done; \
	$(POETRY) run $(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT) --reload $$RELOAD_DIR_FLAGS $$EXCLUDE_FLAGS

## Run server normally (no autoreload)
run:
	@echo "==> Starting server"
	@$(POETRY) run $(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT)

## Run tests, lints, and type checks (skips tools that aren't installed)
test:
	@echo "==> Running tests & code checks"
	$(call run_if_exists,$(RUFF),check .)
	$(call run_if_exists,$(MYPY),src)
	$(call run_if_exists,$(PYTEST),-q)

## Code style (if configured)
lint:
	$(call run_if_exists,$(RUFF),check .)

## Type checks (if configured)
typecheck:
	$(call run_if_exists,$(MYPY),src)

## Auto-format (if configured to use ruff/black)
format:
	$(call run_if_exists,$(RUFF),format .)
	@# If you prefer black, uncomment the next line and add black to dev deps
	@# $(POETRY) run black .

## Export requirements.txt for non-Poetry environments
export-req:
	@echo "==> Exporting requirements.txt"
	@$(POETRY) export -f requirements.txt --without-hashes -o requirements.txt

## Clean local artifacts for a fresh setup
clean:
	@echo "==> Cleaning local artifacts"
	@rm -rf .venv dist build .pytest_cache .mypy_cache .ruff_cache __pycache__ **/__pycache__ *.pyc *.pyo *.log
	@find . -name '*.pyc' -delete -o -name '*.pyo' -delete

## Help: list targets
help:
	@echo ""
	@echo "SeedScape Make targets:"
	@echo "  make install        - Install dependencies (Poetry)"
	@echo "  make install-poetry - Autodetect/Install Poetry"
	@echo "  make dev            - Start dev server with autoreload"
	@echo "  make run            - Start server without autoreload"
	@echo "  make test           - Run tests, lints, type checks"
	@echo "  make lint           - Run linters only"
	@echo "  make typecheck      - Run type checks only"
	@echo "  make format         - Auto-format code (if configured)"
	@echo "  make export-req     - Export requirements.txt"
	@echo "  make clean          - Remove local build/test caches & venv"
	@echo ""
	@echo "Config via .env/.env.local: HOST, PORT, APP_MODULE, RELOAD_DIRS, RELOAD_EXCLUDES"
