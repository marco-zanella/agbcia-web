"""Derives a suggested product code from a ROM's own header.

Real Nintendo Virtual Console titles use a ``CTR-N-`` prefix (an opaque
per-title code follows it, unrelated to the GBA game code). This uses
the same prefix with the 4-character game code as the suffix instead,
distinct from agbcia's own internal auto-derivation (a ``CTR-P-``
prefix) used when the field is left blank at build time.
"""

from __future__ import annotations

_DEFAULT_PRODUCT_CODE = "CTR-N-AGBC"


def default_product_code(game_code: str) -> str:
    if len(game_code) == 4:
        return f"CTR-N-{game_code}"
    return _DEFAULT_PRODUCT_CODE
