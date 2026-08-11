"""``GET /api/lookup/{game_code}``: title_name prefill from the bundled table."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from agbcia_web.deps import get_gamecode_lookup
from agbcia_web.gamecode_lookup import GameCodeLookup
from agbcia_web.schemas import LookupResponse

router = APIRouter()


@router.get("/api/lookup/{game_code}", response_model=LookupResponse)
def lookup_game_code(
    game_code: str,
    lookup: GameCodeLookup = Depends(get_gamecode_lookup),
) -> LookupResponse:
    title_name = lookup.lookup(game_code)
    if title_name is None:
        raise HTTPException(status_code=404, detail=f"no entry for game_code {game_code!r}")
    return LookupResponse(title_name=title_name)
