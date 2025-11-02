from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

HexId = str

Biome = str  # now campaign-defined via meta.json
Feature = Literal["ruins", "village", "tower", "river crossing", "none"]
Encounter = Literal["none", "bandits", "wolves", "travelers"]


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
    # Data-driven biomes per campaign (required; no defaults)
    biomes: list[str]
    # Relative CSS filename within the campaign directory (required; no defaults)
    biomes_css: str


class UserAccount(BaseModel):
    username: str
    password_hash: str
    campaigns: list[str] = Field(default_factory=lambda: list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "0.1"
