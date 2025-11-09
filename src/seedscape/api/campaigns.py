import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import ValidationError

from seedscape.core import storage
from seedscape.core.models import BiomeType, CampaignMeta, EncounterType, FeatureType

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/campaigns", response_model=list[str])
def list_campaigns():
    return storage.list_campaigns()


@router.get("/campaigns/{campaign_name}", response_model=CampaignMeta)
def get_campaign(campaign_name: str) -> CampaignMeta:
    try:
        campaign = storage.load_campaign_meta(campaign_name)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return campaign


@router.get("/campaigns/{campaign_name}/biomes", response_model=list[str])
def get_campaign_biomes(campaign_name: str):
    return [bt.name for bt in get_campaign(campaign_name).biome_types]


@router.get("/campaigns/{campaign_name}/features", response_model=list[str])
def get_campaign_features(campaign_name: str):
    return [ft.name for ft in get_campaign(campaign_name).feature_types]


@router.get("/campaigns/{campaign_name}/encounters", response_model=list[str])
def get_campaign_encounters(campaign_name: str):
    return [et.name for et in get_campaign(campaign_name).encounter_types]


@router.get("/campaigns/{campaign_name}/assets/biomes.css", response_class=PlainTextResponse)
def get_campaign_biomes_css(campaign_name: str):
    css_path = storage.campaign_biomes_css_path(campaign_name)
    if not css_path:
        log.error("Campaign '%s' biomes CSS not found", campaign_name)
        raise HTTPException(status_code=404, detail="CSS not found for campaign")
    return PlainTextResponse(css_path.read_text(encoding="utf-8"), media_type="text/css")


@router.post("/campaigns", response_model=CampaignMeta)
def create_campaign(
    name: Annotated[str, Query(...)],
    biomes: Annotated[list[str], Query(...)],
    biomes_css: Annotated[str, Query(...)],
    features: Annotated[list[str], Query(...)],
    encounters: Annotated[list[str], Query(...)],
) -> CampaignMeta:
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    if not biomes:
        raise HTTPException(status_code=400, detail="biomes is required")
    if not features:
        raise HTTPException(status_code=400, detail="features is required")
    if not encounters:
        raise HTTPException(status_code=400, detail="encounters is required")

    biome_types = [
        BiomeType(
            name=b,
            min_altitude=0,
            max_altitude=1,
            min_temperature=0,
            max_temperature=1,
            min_humidity=0,
            max_humidity=1,
        )
        for b in biomes
    ]
    feature_types = [FeatureType(name=f) for f in features]
    encounter_types = [EncounterType(name=e) for e in encounters]

    try:
        meta = storage.create_campaign(
            name,
            seed=name,  # use name as default seed for API-based creation
            biome_types=biome_types,
            biomes_css=biomes_css,
            feature_types=feature_types,
            encounter_types=encounter_types,
        )
    except Exception as e:  # pydantic validation or storage errors
        raise HTTPException(status_code=500, detail=str(e)) from e
    return meta
