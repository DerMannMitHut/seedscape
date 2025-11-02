import logging

from fastapi import APIRouter, HTTPException

from seedscape.core import generator, storage
from seedscape.core.models import Hex

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/{campaign}/hex/{hex_id}", response_model=Hex)
def get_hex(campaign: str, hex_id: str) -> Hex:
    meta = storage.load_campaign_meta(campaign)
    if not meta:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if not meta.biomes:
        log.error("Campaign '%s' has no biomes configured; cannot generate hex %s", campaign, hex_id)
        raise HTTPException(status_code=500, detail="Campaign has no biomes configured")

    data = storage.load_hex(campaign, hex_id)
    if data:
        return data

    try:
        hex_model = generator.generate_hex(meta.seed, hex_id, biomes=meta.biomes)
    except ValueError as e:
        log.error("Hex generation failed for %s/%s: %s", campaign, hex_id, e)
        raise HTTPException(status_code=500, detail=str(e))
    storage.save_hex(campaign, hex_id, hex_model)
    return hex_model
