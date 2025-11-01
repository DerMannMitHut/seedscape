import random

from seedscape.core.models import Biome, Encounter, Feature, Hex


def generate_hex(seed: str, hex_id: str) -> Hex:
    rnd = random.Random(hash(seed + hex_id))
    biome: Biome = rnd.choice(["forest", "desert", "mountain", "plains", "swamp"])  # type: ignore
    feature: Feature = rnd.choice(["ruins", "village", "tower", "river crossing", "none"])  # type: ignore
    encounter: Encounter = rnd.choice(["none", "bandits", "wolves", "travelers"])  # type: ignore
    return Hex(
        id=hex_id,
        biome=biome,
        feature=feature,
        encounter=encounter,
        discovered=True,
    )
