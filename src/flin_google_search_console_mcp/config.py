from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import os
import sys


REQUIRED_ENV_VARS = (
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
)


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""


def missing_required_env_vars(env: Mapping[str, str] | None = None) -> list[str]:
    source = os.environ if env is None else env
    return [key for key in REQUIRED_ENV_VARS if not source.get(key)]


def default_token_path(
    *, home: Path | None = None, platform_name: str | None = None
) -> Path:
    resolved_home = home or Path.home()
    resolved_platform = platform_name or sys.platform

    if resolved_platform == "darwin":
        return (
            resolved_home
            / "Library"
            / "Application Support"
            / "flin-google-search-console-mcp"
            / "token.json"
        )

    if resolved_platform.startswith("win"):
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "flin-google-search-console-mcp" / "token.json"
        return (
            resolved_home / "AppData" / "Roaming" / "flin-google-search-console-mcp" / "token.json"
        )

    return resolved_home / ".config" / "flin-google-search-console-mcp" / "token.json"


def _parse_oauth_port(raw_value: str | None) -> int:
    if raw_value is None or not raw_value.strip():
        return 0

    try:
        parsed = int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(
            f"Invalid GOOGLE_SEARCH_CONSOLE_OAUTH_PORT value: {raw_value!r}."
        ) from exc

    if parsed < 0 or parsed > 65535:
        raise ConfigurationError(
            f"GOOGLE_SEARCH_CONSOLE_OAUTH_PORT must be between 0 and 65535, got {parsed}."
        )

    return parsed


@dataclass(frozen=True)
class Settings:
    client_id: str
    client_secret: str
    default_site_url: str | None
    token_path: Path
    oauth_port: int


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    source = os.environ if env is None else env
    missing = missing_required_env_vars(source)
    if missing:
        missing_fmt = ", ".join(missing)
        raise ConfigurationError(
            "Missing required environment variables: "
            f"{missing_fmt}. See README.md for setup instructions."
        )

    token_override = source.get("GOOGLE_SEARCH_CONSOLE_TOKEN_PATH")
    token_path = (
        Path(token_override).expanduser()
        if token_override
        else default_token_path()
    )

    default_site_url = source.get("GOOGLE_SEARCH_CONSOLE_SITE_URL")
    default_site_url = default_site_url.strip() if default_site_url else None

    return Settings(
        client_id=source["GOOGLE_CLIENT_ID"].strip(),
        client_secret=source["GOOGLE_CLIENT_SECRET"].strip(),
        default_site_url=default_site_url,
        token_path=token_path,
        oauth_port=_parse_oauth_port(source.get("GOOGLE_SEARCH_CONSOLE_OAUTH_PORT")),
    )
