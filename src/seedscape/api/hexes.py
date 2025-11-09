import logging

from fastapi import APIRouter, HTTPException

from seedscape.core import generator, storage
from seedscape.core.models import Hex

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/{campaign_name}/hex/{hex_id}", response_model=Hex)
def get_hex(campaign_name: str, hex_id: str) -> Hex:
    data = storage.load_hex(campaign_name, hex_id)
    if data:
        return data

    campaign = storage.load_campaign_meta(campaign_name)
    try:
        hex_model = generator.generate_hex(campaign, hex_id)
        storage.save_hex(campaign_name, hex_id, hex_model)
        return hex_model
    except RuntimeError as e:
        log.error("Hex generation failed for %s/%s: %s", campaign_name, hex_id, e)
        raise HTTPException(status_code=500, detail=str(e)) from e
