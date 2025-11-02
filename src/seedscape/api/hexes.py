from fastapi import APIRouter, HTTPException

from seedscape.core import generator, storage
from seedscape.core.models import Hex

router = APIRouter()


@router.get("/{campaign}/hex/{hex_id}", response_model=Hex)
def get_hex(campaign: str, hex_id: str) -> Hex:
    meta = storage.load_campaign_meta(campaign)
    if not meta:
        raise HTTPException(status_code=404, detail="Campaign not found")

    data = storage.load_hex(campaign, hex_id)
    if data:
        return data

    hex_model = generator.generate_hex(meta.seed, hex_id, biomes=meta.biomes)
    storage.save_hex(campaign, hex_id, hex_model)
    return hex_model
