from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

HexId = str

Biome = str  # campaign-defined via meta.json
Feature = str  # campaign-defined via meta.json
Encounter = str  # campaign-defined via meta.json


class Hex(BaseModel):
    id: HexId
    biome: Biome
    feature: Feature = "none"
    encounter: Encounter = "none"
    discovered: bool = False
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "0.1"

    @field_validator("id", mode="before")
    @classmethod
    def validate_hex_id(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("hex id must be non-empty string")
        return v


class CampaignMeta(BaseModel):
    name: str
    seed: str
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "0.1"
    biomes: list[str]
    biomes_css: str
    features: list[str]
    encounters: list[str]


class UserAccount(BaseModel):
    username: str
    password_hash: str
    campaigns: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "0.1"
