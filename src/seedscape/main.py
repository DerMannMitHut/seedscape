from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from seedscape.api import campaigns, hexes

app = FastAPI(title="Seedscape", version="0.1")

app.include_router(hexes.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")

def _detect_frontend_dir() -> Path:
    env = os.getenv("SEEDSCAPE_FRONTEND_DIR")
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p

    repo_root = Path(__file__).resolve().parents[2]
    candidate = repo_root / "frontend"
    if candidate.exists():
        return candidate

    return Path.cwd() / "frontend"

frontend_dir = _detect_frontend_dir()
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

