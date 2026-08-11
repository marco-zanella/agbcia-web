# agbcia-web

A web UI for [agbcia](https://github.com/marco-zanella/agbcia): a form and a
live preview around GBA-to-3DS-CIA injection, for people who'd rather not use
a terminal.

## What this does

- One page: upload a GBA ROM plus icon/banner/badge images and a banner
  sound, fill in the title fields, and download a finished `.cia`.
- A live preview of the animated banner (a spinning box textured with your
  box art and shell color, plus the bottom-screen badge and the banner
  sound) that updates as you edit the form, before you build anything.
- A QR code pointing at the finished CIA's download link, for installing on
  a 3DS over FBI's "Remote install > From QR" without moving files by hand.
- Prefills the title name (via a bundled game-code table) and a valid title
  ID (deterministically derived from the ROM header) when a ROM is
  uploaded; both are freely editable, each with its own reset-to-suggestion
  button.

Uploaded ROMs, images, and audio are never written to disk: they're read
into memory, handed to `agbcia`, and dropped once the request completes.
Only the finished CIA is kept, in memory, for a configurable window so it
can be downloaded.

## Requirements

- Python 3.12 or later.
- Four files this project never bundles or lets you upload through the
  browser, each pointed at by its own `.env` setting:
  - an ARM9 bootROM dump (`boot9.bin`/`boot9_prot.bin`)
  - an extracted AGB_FIRM boot logo, produced once via
    `agbcia footer extract-logo` (native mode)
  - a donor GBA Virtual Console banner, extracted from a donor CIA's ExeFS
    (both modes)
  - a working forwarder/emulator CIA (homebrew mode)

  See [agbcia's own README](https://github.com/marco-zanella/agbcia#readme)
  for where to get these.

## Setup

```sh
uv sync
cp .env.example .env
# edit .env: set BOOT9_PATH, BOOT_LOGO_PATH, DONOR_BANNER_PATH, EMULATOR_CORE_PATH
uv run agbcia-web
```

The app listens on `HOST`/`PORT` from `.env` (default `0.0.0.0:8000`). Open
it from the same address your 3DS can reach on your LAN, not `localhost` --
the QR code encodes whatever address you're browsing from.

## Development

```sh
uv sync --dev
uv run pytest
uv run mypy src
uv run ruff check src tests
```

## Third-party data and code

- `src/agbcia_web/data/gamecodes.json` is built from
  [Gekkio/gb-hardware-db](https://github.com/Gekkio/gb-hardware-db)'s
  `config/games.json` (CC0-1.0), filtered to GBA titles and keyed by the
  4-character game code.
- `src/agbcia_web/static/js/vendor/` carries unmodified builds of
  [Vue](https://vuejs.org/) and [Three.js](https://threejs.org/) (both
  MIT-licensed), vendored so the app runs without a bundler or a CDN.
