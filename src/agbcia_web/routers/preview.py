"""Stateless preview endpoints: nothing they read is persisted anywhere.

``rom-info`` parses an uploaded ROM's header in memory and returns the
detected fields plus prefill suggestions: title_name from the bundled
game-code table, title_id from the deterministic hash, and product_code
from the game code directly.
``crop`` fits an uploaded image to one of the exact target dimensions
agbcia itself will use, so the live preview matches the real output.
"""

from __future__ import annotations

from io import BytesIO
from typing import Literal

from agbcia.banner.image import fit_cover, load_image
from agbcia.formats.smdh import ICON_LARGE_DIMENSIONS, ICON_SMALL_DIMENSIONS
from agbcia.gba.rom_header import parse_header
from agbcia.gba.rtc import detect_rtc
from agbcia.gba.save_type import detect_save_type
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response

from agbcia_web.assets import DonorTextureDims
from agbcia_web.deps import get_donor_texture_dims, get_gamecode_lookup
from agbcia_web.gamecode_lookup import GameCodeLookup
from agbcia_web.product_code import default_product_code
from agbcia_web.schemas import RomInfoResponse
from agbcia_web.title_id_hash import default_title_id

router = APIRouter()

CropKind = Literal["icon_small", "icon_large", "box_art", "badge"]


@router.post("/api/preview/rom-info", response_model=RomInfoResponse)
async def rom_info(
    rom: UploadFile = File(...),
    lookup: GameCodeLookup = Depends(get_gamecode_lookup),
) -> RomInfoResponse:
    rom_bytes = await rom.read()
    header = parse_header(rom_bytes)
    title_id = default_title_id(header.game_code, header.maker_code)
    return RomInfoResponse(
        title=header.title,
        game_code=header.game_code,
        maker_code=header.maker_code,
        checksum_valid=header.checksum_valid,
        detected_save_type=detect_save_type(rom_bytes),
        detected_rtc_present=detect_rtc(rom_bytes),
        suggested_title_id=title_id.hex(),
        suggested_title_name=lookup.lookup(header.game_code),
        suggested_product_code=default_product_code(header.game_code),
    )


@router.post("/api/preview/crop")
async def crop_preview(
    kind: CropKind = Form(...),
    image: UploadFile = File(...),
    donor_dims: DonorTextureDims = Depends(get_donor_texture_dims),
) -> Response:
    source = load_image(await image.read())
    if kind == "icon_small":
        fitted = fit_cover(source.convert("RGB"), *ICON_SMALL_DIMENSIONS)
    elif kind == "icon_large":
        fitted = fit_cover(source.convert("RGB"), *ICON_LARGE_DIMENSIONS)
    elif kind == "box_art":
        fitted = fit_cover(source.convert("RGBA"), *donor_dims.box_art)
    else:
        fitted = fit_cover(source.convert("LA"), *donor_dims.badge)

    buffer = BytesIO()
    fitted.save(buffer, format="PNG")
    return Response(content=buffer.getvalue(), media_type="image/png")
