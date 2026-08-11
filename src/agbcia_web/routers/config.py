"""``GET /api/config``: static values the frontend needs to render the form."""

from __future__ import annotations

from agbcia.gba.save_type import SaveType
from fastapi import APIRouter, Depends

from agbcia_web.config import Settings
from agbcia_web.deps import get_settings
from agbcia_web.schemas import ConfigResponse

router = APIRouter()


@router.get("/api/config", response_model=ConfigResponse)
def get_config(settings: Settings = Depends(get_settings)) -> ConfigResponse:
    return ConfigResponse(
        save_types=list(SaveType),
        result_ttl_seconds=settings.result_ttl_seconds,
    )
