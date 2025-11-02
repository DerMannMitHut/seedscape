import logging
import random
import string

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from seedscape.core import storage
from seedscape.core.models import CampaignMeta

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/campaigns", response_model=list[str])
def list_campaigns():
    return storage.list_campaigns()


@router.get("/campaigns/{campaign}", response_model=CampaignMeta)
def get_campaign(campaign: str):
    meta = storage.load_campaign_meta(campaign)
    if not meta:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return meta


@router.post("/campaigns", response_model=CampaignMeta)
def create_campaign(
    name: Annotated[str, Query(..., min_length=1)],
    biomes: Annotated[list[str], Query(..., min_items=1, description="List of biome keys (repeat param)")],
    biomes_css: Annotated[str, Query(..., min_length=1, description="Relative CSS filename, e.g., biomes.css")],
    features: Annotated[list[str], Query(..., min_items=1, description="List of feature keys (repeat param)")],
    encounters: Annotated[list[str], Query(..., min_items=1, description="List of encounter keys (repeat param)")],
):
    if storage.campaign_exists(name):
        raise HTTPException(status_code=400, detail="Campaign already exists")
    seed = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    return storage.create_campaign(
        name,
        seed,
        biomes=biomes,
        biomes_css=biomes_css,
        features=features,
        encounters=encounters,
    )


@router.get("/campaigns/{campaign}/biomes", response_model=list[str])
def get_campaign_biomes(campaign: str):
    meta = storage.load_campaign_meta(campaign)
    if not meta:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if not meta.biomes:
        log.error("Campaign '%s' has no biomes configured", campaign)
        raise HTTPException(status_code=500, detail="Campaign has no biomes configured")
    return meta.biomes


@router.get("/campaigns/{campaign}/features", response_model=list[str])
def get_campaign_features(campaign: str):
    meta = storage.load_campaign_meta(campaign)
    if not meta:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if not meta.features:
        log.error("Campaign '%s' has no features configured", campaign)
        raise HTTPException(status_code=500, detail="Campaign has no features configured")
    return meta.features


@router.get("/campaigns/{campaign}/encounters", response_model=list[str])
def get_campaign_encounters(campaign: str):
    meta = storage.load_campaign_meta(campaign)
    if not meta:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if not meta.encounters:
        log.error("Campaign '%s' has no encounters configured", campaign)
        raise HTTPException(status_code=500, detail="Campaign has no encounters configured")
    return meta.encounters


@router.get("/campaigns/{campaign}/assets/biomes.css", response_class=PlainTextResponse)
def get_campaign_biomes_css(campaign: str):
    css_path = storage.campaign_biomes_css_path(campaign)
    if not css_path:
        log.error("Campaign '%s' biomes CSS not found", campaign)
        raise HTTPException(status_code=404, detail="CSS not found for campaign")
    return PlainTextResponse(css_path.read_text(encoding="utf-8"), media_type="text/css")
