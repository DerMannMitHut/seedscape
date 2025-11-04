from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient


def make_client(tmp_path: Path) -> TestClient:
    # Configure env for data/frontend before importing app
    import os

    os.environ["SEEDSCAPE_DATA_DIR"] = str(tmp_path)
    # Use real frontend so static mount works
    os.environ["SEEDSCAPE_FRONTEND_DIR"] = str((Path(__file__).resolve().parents[1] / "frontend").resolve())

    import seedscape.api.campaigns as campaigns
    import seedscape.api.hexes as hexes
    import seedscape.core.envconfig as envconfig
    import seedscape.core.storage as storage
    import seedscape.main as main

    importlib.reload(envconfig)
    importlib.reload(storage)
    importlib.reload(campaigns)
    importlib.reload(hexes)
    main = importlib.reload(main)
    return TestClient(main.app)


def test_campaign_endpoints(tmp_path):
    client = make_client(tmp_path)

    # Initially empty
    r = client.get("/api/campaigns")
    assert r.status_code == 200 and r.json() == []

    params = [
        ("name", "testcamp"),
        ("biomes", "forest"),
        ("biomes", "plains"),
        ("biomes_css", "biomes.css"),
        ("features", "none"),
        ("features", "ruins"),
        ("encounters", "none"),
        ("encounters", "bandits"),
    ]
    r = client.post("/api/campaigns", params=params)
    assert r.status_code == 200
    meta = r.json()
    assert meta["name"] == "testcamp"

    # Listing shows new campaign
    r = client.get("/api/campaigns")
    assert "testcamp" in r.json()

    # Biomes list
    r = client.get("/api/campaigns/testcamp/biomes")
    assert r.status_code == 200 and set(r.json()) == {"forest", "plains"}

    # CSS missing -> 404
    r = client.get("/api/campaigns/testcamp/assets/biomes.css")
    assert r.status_code == 404

    # Create CSS and fetch again
    css_path = tmp_path / "campaigns" / "testcamp" / "biomes.css"
    css_path.write_text(".hex.forest { fill: #0f0; }", encoding="utf-8")
    r = client.get("/api/campaigns/testcamp/assets/biomes.css")
    assert r.status_code == 200
    assert ".hex.forest" in r.text


def test_hex_endpoint(tmp_path):
    client = make_client(tmp_path)

    # Create minimal campaign via API
    params = [
        ("name", "c2"),
        ("biomes", "b1"),
        ("biomes_css", "biomes.css"),
        ("features", "f1"),
        ("encounters", "e1"),
    ]
    r = client.post("/api/campaigns", params=params)
    assert r.status_code == 200

    # Request hex
    r = client.get("/api/c2/hex/A1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "A1"
    assert data["biome"] == "b1"
