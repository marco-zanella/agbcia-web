"""App configuration, loaded from the environment and a local ``.env``
file via pydantic-settings. Every field is a required setting; an unset
one raises a validation error at startup.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    #: ARM9 bootROM dump (boot9.bin/boot9_prot.bin).
    boot9_path: Path
    #: Extracted AGB_FIRM boot logo, used in native mode.
    boot_logo_path: Path
    #: Donor GBA Virtual Console banner, used in both modes.
    donor_banner_path: Path
    #: Forwarder/emulator core CIA, used in homebrew mode.
    emulator_core_path: Path

    #: How long a generated CIA stays downloadable after being built.
    result_ttl_seconds: int = 2 * 60 * 60

    #: How often the expired-result sweep runs.
    cleanup_interval_seconds: int = 10 * 60

    #: Total bytes of generated CIAs kept in memory before the oldest ones
    #: are evicted, regardless of TTL.
    max_store_bytes: int = 512 * 1024 * 1024

    host: str = "0.0.0.0"
    port: int = 8000
