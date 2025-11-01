from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from seedscape.api import campaigns, hexes
from seedscape.core.envconfig import SEEDSCAPE_FRONTEND_DIR

app = FastAPI(title="Seedscape", version="0.1")

app.include_router(hexes.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")

frontend_dir = SEEDSCAPE_FRONTEND_DIR
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

