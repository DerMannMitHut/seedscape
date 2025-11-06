from __future__ import annotations

from datetime import datetime, timezone

import pytest

from seedscape.core import generator


def test_generate_hex_uses_lists_and_is_deterministic():
    seed = "abc"
    hex_id = "H4"
    biomes = ["x", "y"]
    features = ["f1", "f2"]
    encounters = ["e1", "e2"]

    fixed_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    h1 = generator.generate_hex(seed, hex_id, biomes=biomes, features=features, encounters=encounters, now=fixed_now)
    h2 = generator.generate_hex(seed, hex_id, biomes=biomes, features=features, encounters=encounters, now=fixed_now)

    assert h1 == h2
    assert h1.biome in biomes
    assert h1.feature in features
    assert h1.encounter in encounters


@pytest.mark.parametrize(
    "kwargs, msg",
    [
        ({"features": ["f"], "encounters": ["e"]}, "biomes"),
        ({"biomes": ["b"], "encounters": ["e"]}, "features"),
        ({"biomes": ["b"], "features": ["f"]}, "encounters"),
    ],
)
def test_generate_hex_fail_fast_on_missing_lists(kwargs, msg):
    with pytest.raises(ValueError) as ei:
        generator.generate_hex("s", "I5", **kwargs)
    assert msg in str(ei.value)
