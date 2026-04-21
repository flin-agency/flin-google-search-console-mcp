from __future__ import annotations

from pathlib import Path
import os

import pytest

from flin_google_search_console_mcp.config import (
    ConfigurationError,
    default_token_path,
    load_settings,
    missing_required_env_vars,
)


def test_missing_required_env_vars_detects_all_missing() -> None:
    missing = missing_required_env_vars(env={})
    assert "GOOGLE_CLIENT_ID" in missing
    assert "GOOGLE_CLIENT_SECRET" in missing


def test_missing_required_env_vars_with_complete_env() -> None:
    env = {
        "GOOGLE_CLIENT_ID": "client-id",
        "GOOGLE_CLIENT_SECRET": "client-secret",
    }
    assert missing_required_env_vars(env=env) == []


def test_default_token_path_uses_macos_application_support() -> None:
    path = default_token_path(home=Path("/Users/tester"), platform_name="darwin")
    assert (
        path
        == Path(
            "/Users/tester/Library/Application Support/flin-google-search-console-mcp/token.json"
        )
    )


def test_default_token_path_uses_xdg_style_on_linux() -> None:
    path = default_token_path(home=Path("/home/tester"), platform_name="linux")
    assert (
        path
        == Path("/home/tester/.config/flin-google-search-console-mcp/token.json")
    )


def test_load_settings_uses_custom_token_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("GOOGLE_SEARCH_CONSOLE_TOKEN_PATH", "/tmp/custom-token.json")

    settings = load_settings()

    assert settings.token_path == Path("/tmp/custom-token.json")


def test_load_settings_reads_optional_default_site(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("GOOGLE_SEARCH_CONSOLE_SITE_URL", "sc-domain:example.com")

    settings = load_settings()

    assert settings.default_site_url == "sc-domain:example.com"


def test_load_settings_rejects_invalid_oauth_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("GOOGLE_SEARCH_CONSOLE_OAUTH_PORT", "abc")

    with pytest.raises(ConfigurationError):
        load_settings()


def test_load_settings_caches_by_environment_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "client-secret")
    first = load_settings()

    monkeypatch.setenv("GOOGLE_SEARCH_CONSOLE_SITE_URL", "https://example.com/")
    second = load_settings()

    assert second.default_site_url == "https://example.com/"
    assert first != second


@pytest.fixture(autouse=True)
def clear_related_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_SEARCH_CONSOLE_SITE_URL",
        "GOOGLE_SEARCH_CONSOLE_TOKEN_PATH",
        "GOOGLE_SEARCH_CONSOLE_OAUTH_PORT",
    ):
        monkeypatch.delenv(key, raising=False)

    os.environ.pop("GOOGLE_CLIENT_ID", None)
