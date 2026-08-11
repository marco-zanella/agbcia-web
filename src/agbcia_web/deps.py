"""FastAPI dependency accessors for state set up in :mod:`agbcia_web.main`'s lifespan."""

from __future__ import annotations

from fastapi import Request

from agbcia_web.assets import DonorTextureDims, FixedAssets
from agbcia_web.config import Settings
from agbcia_web.gamecode_lookup import GameCodeLookup
from agbcia_web.store import ResultStore


def get_settings(request: Request) -> Settings:
    return request.app.state.settings  # type: ignore[no-any-return]


def get_fixed_assets(request: Request) -> FixedAssets:
    return request.app.state.fixed_assets  # type: ignore[no-any-return]


def get_donor_texture_dims(request: Request) -> DonorTextureDims:
    return request.app.state.donor_texture_dims  # type: ignore[no-any-return]


def get_gamecode_lookup(request: Request) -> GameCodeLookup:
    return request.app.state.gamecode_lookup  # type: ignore[no-any-return]


def get_default_banner_sound(request: Request) -> bytes | None:
    return request.app.state.default_banner_sound  # type: ignore[no-any-return]


def get_result_store(request: Request) -> ResultStore:
    return request.app.state.result_store  # type: ignore[no-any-return]
