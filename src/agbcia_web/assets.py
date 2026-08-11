"""Reads the fixed assets pointed at by :class:`agbcia_web.config.Settings`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agbcia.formats import cbmd, cgfx, lz11

from agbcia_web.config import Settings

#: Texture names within a donor banner's CGFX -- see agbcia.banner.donor.
_BOX_ART_TEXTURE_NAME = "COMMON1"
_BOTTOM_BADGE_TEXTURE_NAME = "COMMON2"


@dataclass(frozen=True, slots=True)
class FixedAssets:
    """The four fixed asset files, loaded once at startup."""

    boot9: bytes
    boot_logo: bytes
    donor_banner: bytes
    emulator_core: bytes


@dataclass(frozen=True, slots=True)
class DonorTextureDims:
    """Pixel dimensions of a donor banner's patchable textures."""

    box_art: tuple[int, int]
    badge: tuple[int, int]


def _read(path: Path, label: str) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found at {path}")
    return path.read_bytes()


def load_fixed_assets(settings: Settings) -> FixedAssets:
    """Read all four fixed asset files from the paths in ``settings``."""
    return FixedAssets(
        boot9=_read(settings.boot9_path, "boot9"),
        boot_logo=_read(settings.boot_logo_path, "boot_logo"),
        donor_banner=_read(settings.donor_banner_path, "donor_banner"),
        emulator_core=_read(settings.emulator_core_path, "emulator_core"),
    )


def donor_texture_dims(donor_banner: bytes) -> DonorTextureDims:
    """Read the box-art and badge texture dimensions out of ``donor_banner``'s CGFX."""
    donor_cgfx = lz11.decompress(cbmd.extract_common_cgfx(donor_banner))
    box_art = cgfx.find_texture(donor_cgfx, _BOX_ART_TEXTURE_NAME)
    badge = cgfx.find_texture(donor_cgfx, _BOTTOM_BADGE_TEXTURE_NAME)
    return DonorTextureDims(
        box_art=(box_art.width, box_art.height),
        badge=(badge.width, badge.height),
    )
