import random
import string

from fastapi import APIRouter, HTTPException, Query

from seedscape.core import storage
from seedscape.core.models import CampaignMeta

router = APIRouter()


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
def create_campaign(name: str = Query(..., min_length=1)):
    if storage.campaign_exists(name):
        raise HTTPException(status_code=400, detail="Campaign already exists")
    seed = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    return storage.create_campaign(name, seed)
