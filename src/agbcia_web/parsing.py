"""Parses the hex-string form fields the build form submits."""

from __future__ import annotations


def parse_title_id(value: str) -> bytes:
    """Parse a 16-hex-digit ``title_id`` string into 8 bytes."""
    title_id = bytes.fromhex(value)
    if len(title_id) != 8:
        raise ValueError(f"title_id must be 8 bytes (16 hex chars), got {len(title_id)}")
    return title_id


def parse_hex_color(value: str) -> tuple[int, int, int]:
    """Parse an ``RRGGBB`` hex string into an ``(red, green, blue)`` tuple."""
    color = bytes.fromhex(value)
    if len(color) != 3:
        raise ValueError(f"color must be 3 bytes (6 hex chars, RRGGBB), got {len(color)}")
    return color[0], color[1], color[2]
