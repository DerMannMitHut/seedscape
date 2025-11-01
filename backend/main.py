from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api import hexes, campaigns

app = FastAPI(title="Seedscape", version="0.1")

# Routen registrieren
app.include_router(hexes.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")

# Frontend-Ordner bereitstellen
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
