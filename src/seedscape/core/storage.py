from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from seedscape.core.models import CampaignMeta, Hex


def _detect_data_dir() -> Path:
    env = os.getenv("SEEDSCAPE_DATA_DIR")
    if env:
        p = Path(env).expanduser().resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p
    repo_root = Path(__file__).resolve().parents[3]
    data = repo_root / "data"
    data.mkdir(parents=True, exist_ok=True)
    return data

DATA_DIR = _detect_data_dir()
CAMPAIGNS_DIR = DATA_DIR / "campaigns"

def _campaign_path(name: str) -> Path:
    return CAMPAIGNS_DIR / name

def list_campaigns() -> List[str]:
    if not CAMPAIGNS_DIR.exists():
        return []
    return [p.name for p in CAMPAIGNS_DIR.iterdir() if p.is_dir()]

def campaign_exists(name: str) -> bool:
    return _campaign_path(name).exists()

def create_campaign(name: str, seed: str) -> CampaignMeta:
    path = _campaign_path(name)
    (path / "hexes").mkdir(parents=True, exist_ok=True)
    meta = CampaignMeta(name=name, seed=seed)
    save_campaign_meta(meta)
    return meta

def load_campaign_meta(campaign: str) -> Optional[CampaignMeta]:
    path = _campaign_path(campaign) / "meta.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return CampaignMeta.model_validate(data)

def save_campaign_meta(meta: CampaignMeta) -> None:
    path = _campaign_path(meta.name)
    path.mkdir(parents=True, exist_ok=True)
    (path / "meta.json").write_text(meta.model_dump_json(indent=2), encoding="utf-8")

def _hex_path(campaign: str, hex_id: str) -> Path:
    return _campaign_path(campaign) / "hexes" / f"{hex_id}.json"

def load_hex(campaign: str, hex_id: str) -> Optional[Hex]:
    path = _hex_path(campaign, hex_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return Hex.model_validate(data)

def save_hex(campaign: str, hex_id: str, hex_data: Hex) -> None:
    path = _hex_path(campaign, hex_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(hex_data.model_dump_json(indent=2), encoding="utf-8")
