"""``POST /api/build``: runs the actual agbcia injection.

Every uploaded file is read into memory and handed straight to
``agbcia.inject.pipeline.inject``; only the resulting CIA is kept, in the
in-memory result store, for the download step that follows.
"""

from __future__ import annotations

import asyncio
from typing import Literal

from agbcia.banner.assembly import DEFAULT_PUBLISHER
from agbcia.gba.save_type import SaveType
from agbcia.inject.pipeline import InjectionRequest, inject
from fastapi import APIRouter, Depends, File, Form, UploadFile

from agbcia_web.assets import FixedAssets
from agbcia_web.config import Settings
from agbcia_web.deps import (
    get_default_banner_sound,
    get_fixed_assets,
    get_result_store,
    get_settings,
)
from agbcia_web.parsing import parse_hex_color, parse_title_id
from agbcia_web.schemas import BuildResponse
from agbcia_web.store import ResultStore

router = APIRouter()


def _safe_filename(title_name: str) -> str:
    slug = "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in title_name).strip()
    return f"{slug or 'game'}.cia"


@router.post("/api/build", response_model=BuildResponse)
async def build_cia(
    mode: Literal["native", "homebrew"] = Form(...),
    title_name: str = Form(...),
    title_id: str = Form(...),
    long_title: str | None = Form(None),
    publisher: str = Form(DEFAULT_PUBLISHER),
    save_type: SaveType | None = Form(None),
    rtc_present: bool | None = Form(None),
    product_code: str | None = Form(None),
    title_version: int = Form(0),
    box_shell_color: str | None = Form(None),
    rom: UploadFile = File(...),
    icon: UploadFile = File(...),
    banner_image: UploadFile = File(...),
    bottom_badge: UploadFile | None = File(None),
    banner_sound: UploadFile | None = File(None),
    fixed_assets: FixedAssets = Depends(get_fixed_assets),
    store: ResultStore = Depends(get_result_store),
    settings: Settings = Depends(get_settings),
    default_banner_sound: bytes | None = Depends(get_default_banner_sound),
) -> BuildResponse:
    request = InjectionRequest(
        mode=mode,
        rom=await rom.read(),
        title_id=parse_title_id(title_id),
        title_name=title_name,
        icon_image=await icon.read(),
        banner_image=await banner_image.read(),
        long_title=long_title,
        publisher=publisher,
        banner_sound=(
            await banner_sound.read() if banner_sound is not None else default_banner_sound
        ),
        save_type=save_type,
        rtc_present=rtc_present,
        boot_logo=fixed_assets.boot_logo if mode == "native" else None,
        emulator_core=fixed_assets.emulator_core if mode == "homebrew" else None,
        boot9=fixed_assets.boot9,
        product_code=product_code,
        title_version=title_version,
        donor_banner=fixed_assets.donor_banner,
        bottom_badge_image=await bottom_badge.read() if bottom_badge is not None else None,
        box_shell_color=parse_hex_color(box_shell_color) if box_shell_color else None,
    )
    result = await asyncio.to_thread(inject, request)

    filename = _safe_filename(title_name)
    token, _entry = await store.put(
        result.cia,
        filename,
        metadata={"title_id": result.title_id.hex(), "product_code": result.product_code},
    )
    return BuildResponse(
        token=token,
        filename=filename,
        title_id=result.title_id.hex(),
        product_code=result.product_code,
        save_type=result.save_type,
        rtc_present=result.rtc_present,
        expires_in_seconds=settings.result_ttl_seconds,
    )
