import random

from seedscape.core.models import Biome, Encounter, Feature, Hex


def generate_hex(seed: str, hex_id: str, biomes: list[str] | None = None) -> Hex:
    rnd = random.Random(hash(seed + hex_id))
    choices = biomes or ["forest", "desert", "mountain", "plains", "swamp"]
    biome: Biome = rnd.choice(list(choices))  # type: ignore
    feature: Feature = rnd.choice(["ruins", "village", "tower", "river crossing", "none"])  # type: ignore
    encounter: Encounter = rnd.choice(["none", "bandits", "wolves", "travelers"])  # type: ignore
    return Hex(
        id=hex_id,
        biome=biome,
        feature=feature,
        encounter=encounter,
        discovered=True,
    )
