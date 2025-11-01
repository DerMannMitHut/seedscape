import json, os

BASE_PATH = "data/campaigns"

def load_hex(campaign: str, hex_id: str):
    path = f"{BASE_PATH}/{campaign}/hexes/{hex_id}.json"
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_hex(campaign: str, hex_id: str, data: dict):
    os.makedirs(f"{BASE_PATH}/{campaign}/hexes", exist_ok=True)
    with open(f"{BASE_PATH}/{campaign}/hexes/{hex_id}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_campaign_meta(campaign: str):
    path = f"{BASE_PATH}/{campaign}/meta.json"
    if not os.path.exists(path):
        return None
    return json.load(open(path, "r", encoding="utf-8"))

def list_campaigns():
    base = f"{BASE_PATH}"
    if not os.path.exists(base):
        return []
    return [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]

def campaign_exists(name: str) -> bool:
    return os.path.exists(f"{BASE_PATH}/{name}")

def create_campaign(name: str, seed: str):
    path = f"{BASE_PATH}/{name}"
    os.makedirs(f"{path}/hexes", exist_ok=True)
    meta = {
        "name": name,
        "seed": seed,
        "description": "",
        "created": True
    }
    with open(f"{path}/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
