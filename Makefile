# ==============================
# Seedscape Makefile
# ==============================

# Config
PYTHON := python3
POETRY := poetry
APP := seedscape.main:app
PORT := 8000

# Dirs
SRC_DIR := src
FRONTEND_DIR := frontend
VENV := .venv
DIST := dist

# ========= Helpers =========
# .env automatisch einlesen (exportiert nur KEY=VALUE Zeilen)
ifneq (,$(wildcard .env))
ENV_EXPORT := set -a; . ./.env; set +a;
endif

# ========= Targets =========
.PHONY: help run dev install clean test build setup install-poetry

help:
	@echo "Seedscape – Makefile Befehle:"
	@echo "  make run            Startet Uvicorn mit Reload (src + frontend)"
	@echo "  make dev            Wie run, lädt zusätzlich .env und setzt Debug-Logs"
	@echo "  make install        Poetry-Install der Abhängigkeiten (--sync)"
	@echo "  make clean          Entfernt .venv, dist, Caches"
	@echo "  make test           Führt pytest aus"
	@echo "  make build          Erstellt sdist + wheel (poetry build)"
	@echo "  make install-poetry Installiert Poetry, falls nicht vorhanden"
	@echo "  make setup          install-poetry + install"

# ---------------------------------------
# Server normal (Hot Reload, saubere Excludes)
# ---------------------------------------
run:
	@echo "🚀 Starte Seedscape auf http://127.0.0.1:$(PORT)"
	@$(POETRY) run uvicorn $(APP) \
		--host 127.0.0.1 --port $(PORT) \
		--reload \
		--reload-dir $(SRC_DIR) \
		--reload-dir $(FRONTEND_DIR) \
		--reload-exclude ".venv/*" \
		--reload-exclude "**/site-packages/**" \
		--reload-exclude "**/__pycache__/**" \
		--reload-exclude ".mypy_cache/*" \
		--reload-exclude ".ruff_cache/*"

# ---------------------------------------
# Dev-Server (lädt .env, Debug-Logs)
# ---------------------------------------
dev:
	@echo "🔧 Dev-Modus (lädt .env, Debug-Logs) auf http://127.0.0.1:$(PORT)"
	@$(ENV_EXPORT) \
	$(POETRY) run uvicorn $(APP) \
		--host 127.0.0.1 --port $(PORT) \
		--reload --log-level debug \
		--reload-dir $(SRC_DIR) \
		--reload-dir $(FRONTEND_DIR) \
		--reload-exclude ".venv/*" \
		--reload-exclude "**/site-packages/**" \
		--reload-exclude "**/__pycache__/**" \
		--reload-exclude ".mypy_cache/*" \
		--reload-exclude ".ruff_cache/*"

# ---------------------------------------
# Installation
# ---------------------------------------
install:
	@echo "📦 Poetry install (sync)..."
	@$(POETRY) install --sync

# Einmaliges Setup: Poetry (falls nötig) + install
setup: install-poetry install

# ---------------------------------------
# Poetry Autodetect + Installation
# ---------------------------------------
install-poetry:
	@echo "🔎 Prüfe Poetry..."
	@if command -v poetry >/dev/null 2>&1; then \
		echo "✅ Poetry vorhanden: $$(poetry --version)"; \
	else \
		echo "📥 Installiere Poetry..."; \
		$(PYTHON) - <<'PY' || true ;\
import os, sys, subprocess, shutil; \
url="https://install.python-poetry.org"; \
print("→ Lade Installer:", url); \
subprocess.check_call([sys.executable, "-c", "__import__('urllib.request').urlretrieve('%s','poetry_install.py')" % url]); \
subprocess.check_call([sys.executable, "poetry_install.py"]); \
home = os.path.expanduser("~"); \
local_bin = os.path.join(home, ".local", "bin"); \
print("\nℹ️  Bitte stelle sicher, dass", local_bin, "im PATH ist."); \
print("   z.B.: export PATH=\"$$PATH:%s\"" % local_bin) \
PY \
	; fi

# ---------------------------------------
# Clean / Reset
# ---------------------------------------
clean:
	@echo "🧹 Entferne .venv, dist und Cache-Verzeichnisse ..."
	@rm -rf $(VENV) $(DIST) .mypy_cache .ruff_cache .pytest_cache
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@echo "✅ Clean abgeschlossen."

# ---------------------------------------
# Tests (optional)
# ---------------------------------------
test:
	@echo "🧪 Tests laufen ..."
	@$(POETRY) run pytest -q

# ---------------------------------------
# Build (sdist + wheel)
# ---------------------------------------
build:
	@echo "📦 Baue Distribution ..."
	@$(POETRY) build
