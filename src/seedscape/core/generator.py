import hashlib
import random
from datetime import datetime

from seedscape.core.models import Biome, BiomeType, CampaignMeta, Encounter, EncounterType, Feature, FeatureType, Hex
from seedscape.core.noise import Noise


class Generator:
    def __init__(self, campaign: CampaignMeta):
        self._noise = Noise(campaign)
        self._campaign = campaign


def generate_hex(
    campaign: CampaignMeta,
    hex_id: str,
    *,
    now: datetime | None = None,
) -> Hex:
    seed = campaign.seed
    seed_bytes = f"{seed}:{hex_id}".encode()
    seed_int = int.from_bytes(hashlib.sha256(seed_bytes).digest()[:8], "big")
    rnd = random.Random(seed_int)
    tbiome: BiomeType = rnd.choice(campaign.biome_types)
    tfeature: FeatureType = rnd.choice(campaign.feature_types)
    tencounter: EncounterType = rnd.choice(campaign.encounter_types)

    biome = Biome(
        name=tbiome.name,
        altitude=tbiome.min_altitude,
        temperature=tbiome.min_temperature,
        humidity=tbiome.min_humidity,
    )

    feature = Feature(
        name=tfeature.name,
    )

    encounter = Encounter(
        name=tencounter.name,
    )

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
