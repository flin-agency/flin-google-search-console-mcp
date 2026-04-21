from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .config import Settings, load_settings


SEARCH_CONSOLE_SCOPES = (
    "https://www.googleapis.com/auth/webmasters.readonly",
)


class AuthenticationError(RuntimeError):
    """Raised when credential loading or refresh fails."""


class AuthenticationRequiredError(AuthenticationError):
    """Raised when interactive OAuth is required to continue."""


def _load_token_info(token_path: Path) -> dict[str, Any]:
    try:
        return json.loads(token_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AuthenticationRequiredError(
            f"No token file found at {token_path}."
        ) from exc
    except json.JSONDecodeError as exc:
        raise AuthenticationError(
            f"Token file at {token_path} is not valid JSON."
        ) from exc


def _build_credentials_from_info(
    info: dict[str, Any], scopes: tuple[str, ...]
) -> Any:
    try:
        from google.oauth2.credentials import Credentials
    except ImportError as exc:
        raise AuthenticationError(
            "Google auth dependencies are not installed. Install project dependencies first."
        ) from exc

    try:
        return Credentials.from_authorized_user_info(info, scopes=scopes)
    except Exception as exc:
        raise AuthenticationError("Failed to load credentials from token data.") from exc


def _refresh_credentials(credentials: Any) -> None:
    try:
        from google.auth.transport.requests import Request
    except ImportError as exc:
        raise AuthenticationError(
            "Google auth transport dependency is not installed. Install project dependencies first."
        ) from exc

    credentials.refresh(Request())


def _run_installed_app_flow(settings: Settings) -> Any:
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise AuthenticationError(
            "google-auth-oauthlib is not installed. Install project dependencies first."
        ) from exc

    client_config = {
        "installed": {
            "client_id": settings.client_id,
            "client_secret": settings.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, SEARCH_CONSOLE_SCOPES)
    return flow.run_local_server(
        port=settings.oauth_port,
        open_browser=True,
        access_type="offline",
        prompt="consent",
        authorization_prompt_message=(
            "Open the following URL in your browser to authorize Google Search Console access: {url}"
        ),
        success_message=(
            "Google Search Console authorization complete. You can close this tab and return to Claude Desktop."
        ),
    )


def save_credentials(credentials: Any, token_path: Path) -> None:
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(credentials.to_json(), encoding="utf-8")


def get_credentials(
    *,
    settings: Settings | None = None,
    interactive: bool = True,
) -> Any:
    resolved_settings = settings or load_settings()

    try:
        info = _load_token_info(resolved_settings.token_path)
    except AuthenticationRequiredError:
        if not interactive:
            raise
        credentials = _run_installed_app_flow(resolved_settings)
        save_credentials(credentials, resolved_settings.token_path)
        return credentials

    credentials = _build_credentials_from_info(info, SEARCH_CONSOLE_SCOPES)

    if getattr(credentials, "valid", False):
        return credentials

    if getattr(credentials, "expired", False) and getattr(
        credentials, "refresh_token", None
    ):
        try:
            _refresh_credentials(credentials)
        except Exception as exc:
            if not interactive:
                raise AuthenticationRequiredError(
                    "Stored credentials could not be refreshed and interactive OAuth is required."
                ) from exc
            credentials = _run_installed_app_flow(resolved_settings)

        save_credentials(credentials, resolved_settings.token_path)
        return credentials

    if not interactive:
        raise AuthenticationRequiredError(
            "Interactive OAuth is required to obtain Google Search Console credentials."
        )

    credentials = _run_installed_app_flow(resolved_settings)
    save_credentials(credentials, resolved_settings.token_path)
    return credentials


def describe_auth_state(*, settings: Settings | None = None) -> dict[str, Any]:
    resolved_settings = settings or load_settings()
    token_path = resolved_settings.token_path

    if not token_path.exists():
        return {
            "status": "oauth_required",
            "token_path": str(token_path),
            "has_token_file": False,
        }

    try:
        info = _load_token_info(token_path)
        credentials = _build_credentials_from_info(info, SEARCH_CONSOLE_SCOPES)
    except AuthenticationError as exc:
        return {
            "status": "invalid_token_file",
            "token_path": str(token_path),
            "has_token_file": True,
            "error": str(exc),
        }

    if getattr(credentials, "valid", False):
        status = "ready"
    elif getattr(credentials, "expired", False) and getattr(
        credentials, "refresh_token", None
    ):
        status = "refreshable"
    else:
        status = "oauth_required"

    return {
        "status": status,
        "token_path": str(token_path),
        "has_token_file": True,
    }
