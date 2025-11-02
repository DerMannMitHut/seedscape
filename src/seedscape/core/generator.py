import random

from seedscape.core.models import Biome, Encounter, Feature, Hex


def generate_hex(
    seed: str,
    hex_id: str,
    *,
    biomes: list[str] | None = None,
    features: list[str] | None = None,
    encounters: list[str] | None = None,
) -> Hex:
    rnd = random.Random(hash(seed + hex_id))
    if not biomes:
        raise ValueError("No biomes configured; cannot generate hex biome")
    if not features:
        raise ValueError("No features configured; cannot generate hex feature")
    if not encounters:
        raise ValueError("No encounters configured; cannot generate hex encounter")
    biome: Biome = rnd.choice(list(biomes))  # type: ignore
    feature: Feature = rnd.choice(list(features))  # type: ignore
    encounter: Encounter = rnd.choice(list(encounters))  # type: ignore
    return Hex(
        id=hex_id,
        biome=biome,
        feature=feature,
        encounter=encounter,
        discovered=True,
    )
