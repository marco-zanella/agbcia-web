import pytest
from pydantic import ValidationError

from agbcia_web.config import Settings


def test_settings_requires_all_asset_paths(monkeypatch):
    monkeypatch.delenv("BOOT9_PATH", raising=False)
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            boot_logo_path="x",
            donor_banner_path="x",
            emulator_core_path="x",
        )


def test_settings_reads_explicit_paths(asset_paths):
    settings = Settings()
    assert settings.boot9_path == asset_paths["boot9_path"]
    assert settings.donor_banner_path == asset_paths["donor_banner_path"]


def test_settings_default_ttl_and_cleanup_interval_are_overridable(asset_paths):
    settings = Settings()
    assert settings.result_ttl_seconds == 2
    assert settings.cleanup_interval_seconds == 1
