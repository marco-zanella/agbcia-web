"""Loads the bundled ``data/gamecodes.json`` table for the ``title_name``
prefill."""

from __future__ import annotations

import json
from importlib import resources


class GameCodeLookup:
    """A ``game_code -> title_name`` table, loaded once."""

    def __init__(self, games: dict[str, str]) -> None:
        self._games = games

    def lookup(self, game_code: str) -> str | None:
        return self._games.get(game_code.upper())


def load_default() -> GameCodeLookup:
    """Load the table packaged at ``agbcia_web/data/gamecodes.json``."""
    data_text = (
        resources.files("agbcia_web.data").joinpath("gamecodes.json").read_text(encoding="utf-8")
    )
    payload = json.loads(data_text)
    return GameCodeLookup(payload["games"])
