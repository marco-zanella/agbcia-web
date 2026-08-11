from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agbcia_web.main import create_app
from tests.fixtures import donor_banner_bytes, donor_cia_bytes


@pytest.fixture
def asset_paths(tmp_path, monkeypatch):
    boot9_path = tmp_path / "boot9.bin"
    boot_logo_path = tmp_path / "boot_logo.bin"
    donor_banner_path = tmp_path / "donor_banner.bin"
    emulator_core_path = tmp_path / "emulator_core.cia"

    boot9_path.write_bytes(b"\x00" * 0x10000)
    boot_logo_path.write_bytes(b"\xaa" * 100)
    donor_banner_path.write_bytes(donor_banner_bytes())
    emulator_core_path.write_bytes(donor_cia_bytes())

    monkeypatch.setenv("BOOT9_PATH", str(boot9_path))
    monkeypatch.setenv("BOOT_LOGO_PATH", str(boot_logo_path))
    monkeypatch.setenv("DONOR_BANNER_PATH", str(donor_banner_path))
    monkeypatch.setenv("EMULATOR_CORE_PATH", str(emulator_core_path))
    monkeypatch.setenv("RESULT_TTL_SECONDS", "2")
    monkeypatch.setenv("CLEANUP_INTERVAL_SECONDS", "1")

    return {
        "boot9_path": boot9_path,
        "boot_logo_path": boot_logo_path,
        "donor_banner_path": donor_banner_path,
        "emulator_core_path": emulator_core_path,
    }


@pytest.fixture
def client(asset_paths):
    with TestClient(create_app()) as test_client:
        yield test_client
