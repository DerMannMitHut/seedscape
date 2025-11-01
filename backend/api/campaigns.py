from fastapi import APIRouter, HTTPException
from backend.core import storage
import random, string

router = APIRouter()

@router.get("/campaigns")
def list_campaigns():
    return storage.list_campaigns()

@router.get("/campaigns/{campaign}")
def get_campaign(campaign: str):
    meta = storage.load_campaign_meta(campaign)
    if not meta:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return meta

@router.post("/campaigns")
def create_campaign(name: str):
    seed = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    if storage.campaign_exists(name):
        raise HTTPException(status_code=400, detail="Campaign already exists")
    storage.create_campaign(name, seed)
    return {"name": name, "seed": seed, "status": "created"}
