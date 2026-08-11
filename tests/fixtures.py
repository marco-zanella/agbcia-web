"""Synthetic test fixtures for agbcia-web's own test suite.

Reuses agbcia's public builders directly wherever they exist. The one
exception is a small binary CGFX writer for donor-banner fixtures --
agbcia's own equivalent is a private test helper, not part of its public
API, so this module has its own copy.
"""

from __future__ import annotations

import struct
import wave
from io import BytesIO

from agbcia.formats import cbmd as cbmd_format
from agbcia.formats import cia as cia_format
from agbcia.formats import exefs as exefs_format
from agbcia.formats import exheader as exheader_format
from agbcia.formats import ncch as ncch_format
from agbcia.formats.pica_texture import encode_etc1_solid, encode_la8, encode_rgba8
from agbcia.gba.rom_header import MIN_HEADER_SIZE, compute_header_checksum
from PIL import Image

_TITLE_OFFSET = 0xA0
_GAME_CODE_OFFSET = 0xAC
_MAKER_CODE_OFFSET = 0xB0
_FIXED_VALUE_OFFSET = 0xB2
_CHECKSUM_OFFSET = 0xBD


def build_rom(
    *,
    title: str = "TESTROM",
    game_code: str = "TEST",
    maker_code: str = "01",
    extra: bytes = b"",
) -> bytes:
    """A minimal synthetic GBA ROM: a valid-shape header, zero-padded,
    followed by ``extra`` bytes (e.g. a save-type signature)."""
    rom = bytearray(MIN_HEADER_SIZE)
    rom[_TITLE_OFFSET : _TITLE_OFFSET + 12] = title.encode("ascii").ljust(12, b"\x00")
    rom[_GAME_CODE_OFFSET : _GAME_CODE_OFFSET + 4] = game_code.encode("ascii").ljust(4, b"\x00")
    rom[_MAKER_CODE_OFFSET : _MAKER_CODE_OFFSET + 2] = maker_code.encode("ascii").ljust(2, b"\x00")
    rom[_FIXED_VALUE_OFFSET] = 0x96
    rom[_CHECKSUM_OFFSET] = compute_header_checksum(bytes(rom))
    return bytes(rom) + extra


def png_bytes(
    *, size: tuple[int, int] = (64, 64), color: tuple[int, int, int] = (10, 20, 30)
) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def wav_bytes(*, frames: int = 50) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(22050)
        wav.writeframes((1000).to_bytes(2, "little", signed=True) * frames)
    return buffer.getvalue()


class _ChunkWriter:
    """Appends bytes at a fixed ``base_offset``, tracking named marks and
    self-relative pointers to them -- CGFX's own pointer convention (a
    pointer's value is the byte distance from the pointer field itself
    to its target)."""

    def __init__(self, base_offset: int) -> None:
        self._base_offset = base_offset
        self._buf = bytearray()
        self._fixups: list[tuple[int, str]] = []
        self._marks: dict[str, int] = {}

    def u16(self, value: int) -> None:
        self._buf += value.to_bytes(2, "little")

    def u32(self, value: int) -> None:
        self._buf += (value & 0xFFFFFFFF).to_bytes(4, "little")

    def i32(self, value: int) -> None:
        self._buf += value.to_bytes(4, "little", signed=True)

    def raw(self, data: bytes) -> None:
        self._buf += data

    def mark(self, label: str) -> None:
        self._marks[label] = len(self._buf)

    def pointer_to(self, label: str) -> None:
        self._fixups.append((len(self._buf), label))
        self.u32(0)

    def string(self, label: str, text: str) -> None:
        self.mark(label)
        self.raw(text.encode("ascii") + b"\x00")
        while len(self._buf) % 4:
            self.raw(b"\x00")

    def finish(self) -> bytes:
        for field_offset, label in self._fixups:
            field_abs = self._base_offset + field_offset
            target_abs = self._base_offset + self._marks[label]
            struct.pack_into("<i", self._buf, field_offset, target_abs - field_abs)
        return bytes(self._buf)


def build_synthetic_cgfx(textures: dict[str, tuple[int, int, int, int, bytes]]) -> bytes:
    """A minimal CGFX: a header, a DATA content with just its Textures
    dict slot populated, and one TXOB+Image chunk per entry in
    ``textures``: ``{name: (height, width, hw_format, mipmap_count, raw_buffer)}``.
    """
    w = _ChunkWriter(0)

    w.raw(b"CGFX")
    w.u16(0xFEFF)
    w.u16(0x14)
    w.u32(0x05000000)
    w.u32(0)
    w.u32(1)

    w.raw(b"DATA")
    w.u32(0)
    w.u32(0)
    w.u32(0)
    w.u32(len(textures))
    w.pointer_to("textures_dict")

    w.mark("textures_dict")
    w.raw(b"DICT")
    w.u32(0)
    w.u32(len(textures))
    w.u32(0)
    w.u16(0)
    w.u16(0)
    w.u32(0)
    w.u32(0)
    for name in textures:
        w.u32(0)
        w.u16(0)
        w.u16(0)
        w.pointer_to(f"name_{name}")
        w.pointer_to(f"typechoice_{name}")

    for name, (height, width, hw_format, mipmap_count, raw_buffer) in textures.items():
        w.mark(f"typechoice_{name}")
        w.u32(0x20000011)
        w.raw(b"TXOB")
        w.u32(0x05000000)
        w.pointer_to(f"name_{name}")
        w.u32(0)
        w.u32(0)
        w.i32(height)
        w.i32(width)
        w.u32(0)
        w.u32(0)
        w.i32(mipmap_count)
        w.u32(0)
        w.u32(0)
        w.i32(hw_format)
        w.pointer_to(f"image_{name}")

        w.mark(f"image_{name}")
        w.i32(height)
        w.i32(width)
        w.i32(len(raw_buffer))
        w.pointer_to(f"rawdata_{name}")
        w.u32(0)
        w.i32(0)
        w.u32(0)
        w.u32(0)

        w.mark(f"rawdata_{name}")
        w.raw(raw_buffer)

    for name in textures:
        w.string(f"name_{name}", name)

    return w.finish()


def donor_banner_bytes(*, texture_size: int = 8) -> bytes:
    """A synthetic donor banner (CBMD) with an RGBA8 COMMON1, an LA8
    COMMON2, and an ETC1 COMMON3 texture, each ``texture_size`` square."""
    box_art = encode_rgba8(
        bytes((255, 0, 0, 255)) * (texture_size * texture_size), texture_size, texture_size
    )
    badge = encode_la8(
        bytes((128, 255)) * (texture_size * texture_size), texture_size, texture_size
    )
    shell = encode_etc1_solid((10, 10, 10), texture_size, texture_size)
    donor_cgfx = build_synthetic_cgfx(
        {
            "COMMON1": (texture_size, texture_size, 0, 1, box_art),
            "COMMON2": (texture_size, texture_size, 5, 1, badge),
            "COMMON3": (texture_size, texture_size, 12, 1, shell),
        }
    )
    return cbmd_format.build(cgfx=donor_cgfx, cwav=None)


def donor_cia_bytes(*, code: bytes = b"\xcc" * 300) -> bytes:
    """A synthetic, self-signed forwarder-core CIA usable as ``emulator_core``."""
    title_id = bytes.fromhex("00040000aabbccdd")
    exheader = exheader_format.build(
        exheader_format.ExHeader(
            sci=exheader_format.SystemControlInfo(title_name="COREAPP"),
            local_caps=exheader_format.LocalCapabilities(title_id=title_id),
        )
    )
    exefs = exefs_format.build(
        [
            exefs_format.ExeFSFile(name="icon", data=b"donor-icon-discarded"),
            exefs_format.ExeFSFile(name=".code", data=code),
        ]
    )
    ncch = ncch_format.Ncch(
        title_id=title_id, product_code="CTR-P-CORE", exheader=exheader, exefs=exefs
    )
    return cia_format.build(ticket=b"t" * 10, tmd=b"m" * 10, content=ncch_format.build(ncch))
