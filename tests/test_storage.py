from __future__ import annotations

import importlib
from pathlib import Path

from seedscape.core.models import (
    Biome,
    BiomeType,
    Encounter,
    EncounterType,
    Feature,
    FeatureType,
    Hex,
)


def setup_storage(tmp_path: Path, monkeypatch):
    # Point data dir to tmp and reload modules to rebind constants
    monkeypatch.setenv("SEEDSCAPE_DATA_DIR", str(tmp_path))
    import seedscape.core.envconfig as envconfig
    import seedscape.core.storage as storage

    importlib.reload(envconfig)
    storage = importlib.reload(storage)
    return storage


def test_campaign_lifecycle(tmp_path, monkeypatch):
    storage = setup_storage(tmp_path, monkeypatch)

    assert storage.list_campaigns() == []

    meta = storage.create_campaign(
        "c1",
        seed="s",
        biome_types=[
            BiomeType(
                name="forest",
                min_altitude=0,
                max_altitude=1,
                min_temperature=0,
                max_temperature=1,
                min_humidity=0,
                max_humidity=1,
            ),
            BiomeType(
                name="plains",
                min_altitude=0,
                max_altitude=1,
                min_temperature=0,
                max_temperature=1,
                min_humidity=0,
                max_humidity=1,
            ),
        ],
        biomes_css="biomes.css",
        feature_types=[FeatureType(name="none"), FeatureType(name="ruins")],
        encounter_types=[EncounterType(name="none"), EncounterType(name="bandits")],
    )
    assert meta.name == "c1"
    assert "c1" in storage.list_campaigns()

    loaded = storage.load_campaign_meta("c1")
    assert loaded is not None
    assert loaded.name == "c1"

    # CSS path absent until file exists
    assert storage.campaign_biomes_css_path("c1") is None
    css = storage.CAMPAIGNS_DIR / "c1" / "biomes.css"
    css.write_text(".hex.forest { fill: #0f0; }", encoding="utf-8")
    assert storage.campaign_biomes_css_path("c1") == css


def test_hex_load_save(tmp_path, monkeypatch):
    storage = setup_storage(tmp_path, monkeypatch)

    storage.create_campaign(
        "c2",
        seed="s2",
        biome_types=[
            BiomeType(
                name="a",
                min_altitude=0,
                max_altitude=1,
                min_temperature=0,
                max_temperature=1,
                min_humidity=0,
                max_humidity=1,
            )
        ],
        biomes_css="b.css",
        feature_types=[FeatureType(name="f")],
        encounter_types=[EncounterType(name="e")],
    )
    assert storage.load_hex("c2", "A1") is None

    h = Hex(
        id="A1",
        biome=Biome(name="a", altitude=0.0, temperature=0.0, humidity=0.0),
        features=[Feature(name="f")],
        encounter=Encounter(name="e"),
        discovered=True,
    )
    storage.save_hex("c2", "A1", h)
    got = storage.load_hex("c2", "A1")
    assert got is not None
    assert got.id == "A1"
    assert got.biome.name == "a"
