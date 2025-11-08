import hashlib
import random
from datetime import datetime

from seedscape.core.models import Biome, Encounter, Feature, Hex
from seedscape.core.noise import Noise


class Generator:
    def __init__(self, seed: str, biomes: list[Biome], features: list[Feature], encounters: list[Encounter]):
        self._noise = Noise(seed)
        self._biomes = biomes
        self._features = features
        self._encounters = encounters


def generate_hex(
    seed: str,
    hex_id: str,
    *,
    biomes: list[str] | None = None,
    features: list[str] | None = None,
    encounters: list[str] | None = None,
    now: datetime | None = None,
) -> Hex:
    if not biomes:
        raise ValueError("No biomes configured; cannot generate hex biome")
    if not features:
        raise ValueError("No features configured; cannot generate hex feature")
    if not encounters:
        raise ValueError("No encounters configured; cannot generate hex encounter")

    # Use a stable, deterministic seed derived from input values
    seed_bytes = f"{seed}:{hex_id}".encode()
    seed_int = int.from_bytes(hashlib.sha256(seed_bytes).digest()[:8], "big")
    rnd = random.Random(seed_int)
    biome: Biome = rnd.choice(list(biomes))  # type: ignore
    feature: Feature = rnd.choice(list(features))  # type: ignore
    encounter: Encounter = rnd.choice(list(encounters))  # type: ignore

    if now:
        hex = Hex(
            id=hex_id,
            biome=biome,
            features=[feature],
            encounter=encounter,
            discovered=True,
            created_at=now,
        )
    else:
        hex = Hex(
            id=hex_id,
            biome=biome,
            features=[feature],
            encounter=encounter,
            discovered=True,
        )

    return hex
