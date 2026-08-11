"""FastAPI app entry point: wires config, fixed assets, the result store,
and every router together, and serves the static frontend."""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from agbcia_web import assets
from agbcia_web.config import Settings
from agbcia_web.errors import register_exception_handlers
from agbcia_web.gamecode_lookup import load_default as load_default_gamecode_lookup
from agbcia_web.routers import build, config, download, lookup, preview
from agbcia_web.store import ResultStore, run_cleanup_loop

_STATIC_DIR = Path(__file__).parent / "static"
_DEFAULT_BANNER_SOUND_PATH = _STATIC_DIR / "templates" / "audio-template.wav"


def _load_default_banner_sound() -> bytes | None:
    """The bundled template WAV, used as the banner sound when none is
    uploaded. Returns ``None`` if that template hasn't been added."""
    if _DEFAULT_BANNER_SOUND_PATH.is_file():
        return _DEFAULT_BANNER_SOUND_PATH.read_bytes()
    return None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()  # type: ignore[call-arg]  # fields are read from the environment
    fixed_assets = assets.load_fixed_assets(settings)

    app.state.settings = settings
    app.state.fixed_assets = fixed_assets
    app.state.donor_texture_dims = assets.donor_texture_dims(fixed_assets.donor_banner)
    app.state.default_banner_sound = _load_default_banner_sound()
    app.state.gamecode_lookup = load_default_gamecode_lookup()
    app.state.result_store = ResultStore(
        ttl_seconds=settings.result_ttl_seconds,
        max_bytes=settings.max_store_bytes,
    )

    cleanup_task = asyncio.create_task(
        run_cleanup_loop(app.state.result_store, settings.cleanup_interval_seconds)
    )
    try:
        yield
    finally:
        cleanup_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await cleanup_task


def create_app() -> FastAPI:
    app = FastAPI(title="agbcia-web", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(config.router)
    app.include_router(lookup.router)
    app.include_router(preview.router)
    app.include_router(build.router)
    app.include_router(download.router)
    app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")
    return app


app = create_app()


def run() -> None:
    settings = Settings()  # type: ignore[call-arg]  # fields are read from the environment
    uvicorn.run("agbcia_web.main:app", host=settings.host, port=settings.port)
