from __future__ import annotations

import json
from pathlib import Path

from seedscape.core.envconfig import SEEDSCAPE_DATA_DIR
from seedscape.core.models import BiomeType, CampaignMeta, EncounterType, FeatureType, Hex


def _detect_data_dir() -> Path:
    p = SEEDSCAPE_DATA_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


DATA_DIR = _detect_data_dir()
CAMPAIGNS_DIR = DATA_DIR / "campaigns"


def _campaign_path(name: str) -> Path:
    return CAMPAIGNS_DIR / name


def list_campaigns() -> list[str]:
    if not CAMPAIGNS_DIR.exists():
        return []
    return [p.name for p in CAMPAIGNS_DIR.iterdir() if p.is_dir()]


def campaign_exists(name: str) -> bool:
    return _campaign_path(name).exists()


def create_campaign(
    name: str,
    seed: str,
    biome_types: list[BiomeType],
    biomes_css: str,
    *,
    feature_types: list[FeatureType],
    encounter_types: list[EncounterType],
) -> CampaignMeta:
    path = _campaign_path(name)
    (path / "hexes").mkdir(parents=True, exist_ok=True)
    meta = CampaignMeta(
        name=name,
        seed=seed,
        biome_types=biome_types,
        biomes_css=biomes_css,
        feature_types=feature_types,
        encounter_types=encounter_types,
    )
    save_campaign_meta(meta)
    return meta


def load_campaign_meta(campaign: str) -> CampaignMeta | None:
    path = _campaign_path(campaign) / "meta.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return CampaignMeta.model_validate(data)


def save_campaign_meta(meta: CampaignMeta) -> None:
    path = _campaign_path(meta.name)
    path.mkdir(parents=True, exist_ok=True)
    (path / "meta.json").write_text(meta.model_dump_json(indent=2), encoding="utf-8")


def campaign_biomes_css_path(campaign: str) -> Path | None:
    meta = load_campaign_meta(campaign)
    if not meta:
        return None
    css_path = _campaign_path(campaign) / meta.biomes_css
    return css_path if css_path.exists() else None


# Note: default biomes CSS generation was intentionally removed to avoid hidden defaults.


def _hex_path(campaign: str, hex_id: str) -> Path:
    return _campaign_path(campaign) / "hexes" / f"{hex_id}.json"


def load_hex(campaign: str, hex_id: str) -> Hex | None:
    path = _hex_path(campaign, hex_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return Hex.model_validate(data)


def save_hex(campaign: str, hex_id: str, hex_data: Hex) -> None:
    path = _hex_path(campaign, hex_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(hex_data.model_dump_json(indent=2), encoding="utf-8")
