from agbcia.formats import cia as cia_format

from tests.fixtures import build_rom, png_bytes, wav_bytes

_NATIVE_TITLE_ID = "0004000000f01200"
_HOMEBREW_TITLE_ID = "0004000012345678"


def test_config_endpoint(client):
    response = client.get("/api/config")
    assert response.status_code == 200
    body = response.json()
    assert "none" in body["save_types"]
    assert body["result_ttl_seconds"] == 2


def test_lookup_known_game_code(client):
    response = client.get("/api/lookup/BZ6E")
    assert response.status_code == 200
    assert response.json()["title_name"]


def test_lookup_unknown_game_code_is_404(client):
    response = client.get("/api/lookup/ZZZZ")
    assert response.status_code == 404


def test_rom_info_endpoint(client):
    rom = build_rom(game_code="TEST", extra=b"SRAM_V113")
    response = client.post("/api/preview/rom-info", files={"rom": ("game.gba", rom)})
    assert response.status_code == 200
    body = response.json()
    assert body["game_code"] == "TEST"
    assert body["detected_save_type"] == "sram"
    assert len(body["suggested_title_id"]) == 16
    assert body["suggested_product_code"] == "CTR-N-TEST"


def test_rom_info_rejects_too_short_rom(client):
    response = client.post("/api/preview/rom-info", files={"rom": ("game.gba", b"short")})
    assert response.status_code == 422


def test_crop_preview_returns_png(client):
    response = client.post(
        "/api/preview/crop",
        data={"kind": "icon_small"},
        files={"image": ("icon.png", png_bytes())},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def _build_payload(*, mode: str, title_id: str) -> tuple[dict, dict]:
    data = {
        "mode": mode,
        "title_name": "My Game",
        "title_id": title_id,
        "box_shell_color": "336699",
    }
    files = {
        "rom": ("game.gba", build_rom(game_code="TEST", extra=b"SRAM_V113")),
        "icon": ("icon.png", png_bytes()),
        "banner_image": ("banner.png", png_bytes(size=(64, 32))),
        "banner_sound": ("banner.wav", wav_bytes(), "audio/wav"),
    }
    return data, files


def test_build_native_cia(client):
    data, files = _build_payload(mode="native", title_id=_NATIVE_TITLE_ID)
    response = client.post("/api/build", data=data, files=files)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["title_id"] == _NATIVE_TITLE_ID
    assert body["save_type"] == "sram"

    download = client.get(f"/api/download/{body['token']}")
    assert download.status_code == 200
    assert download.content[0:16] != b""
    cia_format.extract_content(download.content)  # a well-formed CIA parses

    qr = client.get(f"/api/download/{body['token']}/qr")
    assert qr.status_code == 200
    assert qr.headers["content-type"] == "image/png"


def test_build_homebrew_cia(client):
    data, files = _build_payload(mode="homebrew", title_id=_HOMEBREW_TITLE_ID)
    response = client.post("/api/build", data=data, files=files)
    assert response.status_code == 200, response.text
    assert response.json()["title_id"] == _HOMEBREW_TITLE_ID


def test_build_rejects_native_title_id_outside_vc_range(client):
    data, files = _build_payload(mode="native", title_id=_HOMEBREW_TITLE_ID)
    response = client.post("/api/build", data=data, files=files)
    assert response.status_code == 422


def test_download_unknown_token_is_404(client):
    response = client.get("/api/download/does-not-exist")
    assert response.status_code == 404
