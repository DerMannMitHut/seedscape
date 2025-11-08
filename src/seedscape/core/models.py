from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

HexId = str

BiomeName = str


class BiomeType(BaseModel):
    name: BiomeName
    min_altitude: float
    max_altitude: float
    min_temperature: float
    max_temperature: float
    min_humidity: float
    max_humidity: float


class Biome(BaseModel):
    name: BiomeName
    altitude: float
    temperature: float
    humidity: float


FeatureName = str


class FeatureType(BaseModel):
    name: FeatureName


class Feature(BaseModel):
    name: FeatureName


EncounterName = str


class EncounterType(BaseModel):
    name: EncounterName


class Encounter(BaseModel):
    name: EncounterName


class Hex(BaseModel):
    id: HexId
    biome: Biome
    features: list[Feature]
    encounter: Encounter
    discovered: bool = False
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "0.1"

    @field_validator("id")
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
    biome_types: list[BiomeType] = Field(..., min_length=1)
    biomes_css: str
    feature_types: list[FeatureType] = Field(..., min_length=1)
    encounter_types: list[EncounterType] = Field(..., min_length=1)
    base_temperature: float


class UserAccount(BaseModel):
    username: str
    password_hash: str
    campaigns: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "0.1"
