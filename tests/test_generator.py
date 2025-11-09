from __future__ import annotations

from datetime import datetime, timezone

from seedscape.core import generator
from seedscape.core.models import (
    BiomeType,
    CampaignMeta,
    EncounterType,
    FeatureType,
)


def make_campaign(seed: str = "abc") -> CampaignMeta:
    return CampaignMeta(
        name="test",
        seed=seed,
        description="",
        biome_types=[
            BiomeType(
                name="x",
                min_altitude=0,
                max_altitude=10,
                min_temperature=0,
                max_temperature=10,
                min_humidity=0,
                max_humidity=10,
            ),
            BiomeType(
                name="y",
                min_altitude=0,
                max_altitude=10,
                min_temperature=0,
                max_temperature=10,
                min_humidity=0,
                max_humidity=10,
            ),
        ],
        biomes_css="biomes.css",
        feature_types=[FeatureType(name="f1"), FeatureType(name="f2")],
        encounter_types=[EncounterType(name="e1"), EncounterType(name="e2")],
        base_temperature=20.0,
    )


def test_generate_hex_is_deterministic_and_valid_models():
    hex_id = "H4"
    fixed_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    camp = make_campaign()

    h1 = generator.generate_hex(camp, hex_id, now=fixed_now)
    h2 = generator.generate_hex(camp, hex_id, now=fixed_now)

    assert h1 == h2
    assert h1.id == hex_id
    assert h1.discovered is True
    assert h1.created_at == fixed_now
    # Values selected from types lists
    biome_names = {t.name for t in camp.biome_types}
    feature_names = {t.name for t in camp.feature_types}
    encounter_names = {t.name for t in camp.encounter_types}
    assert h1.biome.name in biome_names
    assert h1.features[0].name in feature_names
    assert h1.encounter.name in encounter_names
