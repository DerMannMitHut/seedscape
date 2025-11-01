import random

def generate_hex(seed: str, hex_id: str):
    rnd = random.Random(hash(seed + hex_id))
    biome = rnd.choice(["forest", "desert", "mountain", "plains", "swamp"])
    feature = rnd.choice(["ruins", "village", "tower", "river crossing"])
    encounter = rnd.choice(["none", "bandits", "wolves", "travelers"])
    return {
        "id": hex_id,
        "biome": biome,
        "feature": feature,
        "encounter": encounter,
        "discovered": True
    }
