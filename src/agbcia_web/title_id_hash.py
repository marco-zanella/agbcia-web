"""Derives a default native-mode ``title_id`` from a ROM's own header.

``0004000000F???00`` is the pattern
:func:`agbcia.inject.pipeline.InjectionRequest` requires for native mode;
only the three ``?`` hex digits (12 bits) vary per title, and there is no
public table of Nintendo's own values for them. This module fills those
12 bits with a hash of the ROM header's ``game_code`` and ``maker_code``,
giving a deterministic, always-available suggestion the user can accept
or edit.
"""

from __future__ import annotations

import zlib

_TITLE_ID_PREFIX = bytes.fromhex("0004000000")
_FREE_BITS_MASK = 0xFFF


def default_title_id(game_code: str, maker_code: str) -> bytes:
    """Return the suggested native-mode ``title_id`` for a ROM whose
    header carries ``game_code`` and ``maker_code``."""
    digest = zlib.crc32(game_code.encode("ascii") + maker_code.encode("ascii"))
    free_bits = digest & _FREE_BITS_MASK
    byte5 = 0xF0 | (free_bits >> 8)
    byte6 = free_bits & 0xFF
    return _TITLE_ID_PREFIX + bytes((byte5, byte6, 0x00))
