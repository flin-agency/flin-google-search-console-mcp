from __future__ import annotations

from pathlib import Path
import json

import pytest

from flin_google_search_console_mcp.config import Settings
from flin_google_search_console_mcp import auth


class FakeCredentials:
    def __init__(
        self,
        *,
        valid: bool,
        expired: bool = False,
        refresh_token: str | None = None,
        payload: dict[str, str] | None = None,
    ) -> None:
        self.valid = valid
        self.expired = expired
        self.refresh_token = refresh_token
        self.payload = payload or {"token": "serialized"}
        self.refresh_calls = 0

    def refresh(self, request: object) -> None:
        self.refresh_calls += 1
        self.valid = True
        self.expired = False

    def to_json(self) -> str:
        return json.dumps(self.payload)


def _settings(token_path: Path) -> Settings:
    return Settings(
        client_id="client-id",
        client_secret="client-secret",
        default_site_url="sc-domain:example.com",
        token_path=token_path,
        oauth_port=0,
    )


def test_get_credentials_loads_valid_credentials_from_token_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    token_path = tmp_path / "token.json"
    token_path.write_text('{"token":"cached"}', encoding="utf-8")
    credentials = FakeCredentials(valid=True)

    monkeypatch.setattr(
        auth,
        "_build_credentials_from_info",
        lambda info, scopes: credentials,
    )

    result = auth.get_credentials(settings=_settings(token_path), interactive=False)

    assert result is credentials


def test_get_credentials_refreshes_expired_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    token_path = tmp_path / "token.json"
    token_path.write_text('{"token":"expired"}', encoding="utf-8")
    credentials = FakeCredentials(
        valid=False,
        expired=True,
        refresh_token="refresh-token",
        payload={"token": "refreshed"},
    )

    monkeypatch.setattr(
        auth,
        "_build_credentials_from_info",
        lambda info, scopes: credentials,
    )
    monkeypatch.setattr(auth, "_refresh_credentials", lambda creds: creds.refresh(None))

    result = auth.get_credentials(settings=_settings(token_path), interactive=False)

    assert result is credentials
    assert credentials.refresh_calls == 1
    assert json.loads(token_path.read_text(encoding="utf-8")) == {"token": "refreshed"}


def test_get_credentials_requires_interactive_auth_when_token_file_is_missing(
    tmp_path: Path,
) -> None:
    token_path = tmp_path / "missing-token.json"

    with pytest.raises(auth.AuthenticationRequiredError):
        auth.get_credentials(settings=_settings(token_path), interactive=False)


def test_get_credentials_raises_clean_error_for_corrupted_token_file(
    tmp_path: Path,
) -> None:
    token_path = tmp_path / "token.json"
    token_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(auth.AuthenticationError):
        auth.get_credentials(settings=_settings(token_path), interactive=False)


def test_get_credentials_runs_installed_app_flow_when_interactive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    token_path = tmp_path / "missing-token.json"
    credentials = FakeCredentials(valid=True, payload={"token": "interactive"})

    monkeypatch.setattr(
        auth,
        "_run_installed_app_flow",
        lambda settings: credentials,
    )

    result = auth.get_credentials(settings=_settings(token_path), interactive=True)

    assert result is credentials
    assert json.loads(token_path.read_text(encoding="utf-8")) == {"token": "interactive"}
