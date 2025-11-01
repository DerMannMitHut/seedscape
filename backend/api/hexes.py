from fastapi import APIRouter, HTTPException
from backend.core import generator, storage

router = APIRouter()

@router.get("/{campaign}/hex/{hex_id}")
def get_hex(campaign: str, hex_id: str):
    data = storage.load_hex(campaign, hex_id)
    if data:
        return data
    # Generiere neues Hex, falls nicht vorhanden
    campaign_meta = storage.load_campaign_meta(campaign)
    if not campaign_meta:
        raise HTTPException(status_code=404, detail="Campaign not found")
    hex_data = generator.generate_hex(campaign_meta["seed"], hex_id)
    storage.save_hex(campaign, hex_id, hex_data)
    return hex_data
