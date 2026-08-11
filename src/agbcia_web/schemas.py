"""Pydantic response models for the API."""

from __future__ import annotations

from agbcia.gba.save_type import SaveType
from pydantic import BaseModel


class ConfigResponse(BaseModel):
    save_types: list[SaveType]
    result_ttl_seconds: int


class RomInfoResponse(BaseModel):
    title: str
    game_code: str
    maker_code: str
    checksum_valid: bool
    detected_save_type: SaveType
    detected_rtc_present: bool
    suggested_title_id: str
    suggested_title_name: str | None
    suggested_product_code: str


class LookupResponse(BaseModel):
    title_name: str


class BuildResponse(BaseModel):
    token: str
    filename: str
    title_id: str
    product_code: str
    save_type: SaveType
    rtc_present: bool
    expires_in_seconds: int
