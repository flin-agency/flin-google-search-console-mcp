from __future__ import annotations

from typing import Any, Sequence

from googleapiclient.errors import HttpError

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.exceptions import ToolError
    from mcp.types import ToolAnnotations
except ImportError:
    class ToolAnnotations(dict):  # type: ignore[no-redef]
        pass

    class ToolError(RuntimeError):
        pass

    class FastMCP:  # type: ignore[override]
        def __init__(self, name: str, instructions: str) -> None:
            self.name = name
            self.instructions = instructions

        def tool(self, **kwargs):
            def decorator(func):
                return func

            return decorator

        def run(self) -> None:
            raise RuntimeError(
                "mcp dependency is not installed. Install project dependencies first."
            )

from .auth import AuthenticationError, AuthenticationRequiredError, describe_auth_state
from . import __version__
from .config import ConfigurationError, load_settings, missing_required_env_vars
from .search_console import (
    get_dimension_breakdown as get_dimension_breakdown_data,
    get_site_summary as get_site_summary_data,
    get_top_pages as get_top_pages_data,
    get_top_queries as get_top_queries_data,
    inspect_url as inspect_url_data,
    list_sites as list_sites_data,
    query_performance as query_performance_data,
)


mcp = FastMCP(
    name="flin-google-search-console-mcp",
    instructions=(
        "Read-only MCP server for Google Search Console performance analysis and URL inspection. "
        "No write operations are exposed."
    ),
)


def _tool_error(exc: Exception) -> ToolError:
    """Expose only fixed messages; upstream exceptions can contain credentials or URLs."""
    if isinstance(exc, ConfigurationError):
        message = (
            "invalid_configuration: Check the Google OAuth configuration and account name. "
            "Named accounts must not refer to the default token file; omit account to use it."
        )
    elif isinstance(exc, AuthenticationRequiredError):
        message = "oauth_required: Sign in to the selected Google account and try again."
    elif isinstance(exc, AuthenticationError):
        message = (
            "authentication_failed: Check the saved credentials and token storage. "
            "Use a directory owned by you that other users cannot write to."
        )
    elif isinstance(exc, HttpError):
        status = exc.resp.status
        if status == 401:
            message = "oauth_required: Google rejected the credentials. Sign in again."
        elif status == 403:
            message = (
                "permission_denied: Google denied the request. "
                "Check property access, API enablement, and quota."
            )
        elif status == 429:
            message = "quota_exceeded: Google limited the requests. Try again later."
        elif status >= 500:
            message = "service_unavailable: Google is temporarily unavailable. Try again later."
        else:
            message = "google_request_failed: Google rejected the request. Check the tool arguments."
    elif isinstance(exc, TimeoutError):
        message = "request_timeout: The request timed out. Try again."
    elif isinstance(exc, OSError):
        message = "io_error: Check token storage permissions and network connectivity."
    elif isinstance(exc, ValueError):
        message = (
            "invalid_arguments: Check the dates, property, dimensions, filters, "
            "and pagination values."
        )
    else:
        message = "internal_error: The request failed. Restart the server and try again."
    return ToolError(message)


def _account_payload(account: str | None) -> dict[str, str]:
    if account is None:
        return {}

    normalized = account.strip()
    if not normalized:
        return {}

    return {"account": normalized}


def _read_only_tool(title: str, *, external: bool = True):
    return mcp.tool(annotations=ToolAnnotations(
        title=title,
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=external,
    ))


@_read_only_tool("Check Search Console connection", external=False)
def health_check(account: str | None = None) -> dict[str, Any]:
    """Check local configuration and saved sign-in status without opening a browser or calling Google."""
    missing = missing_required_env_vars()
    if missing:
        return {
            "ok": False,
            "server_version": __version__,
            "status": "missing_configuration",
            "missing_env_vars": missing,
        }

    try:
        settings = load_settings()
        auth_state = describe_auth_state(settings=settings, account=account)
    except Exception as exc:
        raise _tool_error(exc) from None

    return {
        "ok": auth_state["status"] in {"ready", "refreshable"},
        "server_version": __version__,
        **_account_payload(account),
        "status": auth_state["status"],
        "default_site_url": settings.default_site_url,
        "has_token_file": auth_state["has_token_file"],
        "oauth_port": settings.oauth_port,
    }


@_read_only_tool("List Search Console properties")
def list_sites(account: str | None = None) -> dict[str, Any]:
    """List properties available to the selected Google account before choosing a site to analyse.

    Opens Google sign-in in the browser if needed and saves or refreshes the local token.
    Does not modify Search Console properties.
    """
    try:
        result = list_sites_data(account=account)
        return {"ok": True, **result}
    except Exception as exc:
        raise _tool_error(exc) from None


@_read_only_tool("Summarise Search Console performance")
def get_site_summary(
    start_date: str,
    end_date: str,
    site_url: str | None = None,
    search_type: str = "web",
    data_state: str | None = None,
    account: str | None = None,
) -> dict[str, Any]:
    """Get aggregate performance metrics for a property over a date range."""
    try:
        result = get_site_summary_data(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            search_type=search_type,
            data_state=data_state,
            account=account,
        )
        return {"ok": True, **result}
    except Exception as exc:
        raise _tool_error(exc) from None


@_read_only_tool("Query Search Console performance")
def query_performance(
    start_date: str,
    end_date: str,
    site_url: str | None = None,
    dimensions: Sequence[str] | None = None,
    search_type: str = "web",
    aggregation_type: str | None = None,
    data_state: str | None = None,
    row_limit: int = 1000,
    start_row: int = 0,
    filters: list[dict[str, str]] | None = None,
    account: str | None = None,
) -> dict[str, Any]:
    """Query Search Analytics performance data with explicit dimensions and filters."""
    try:
        result = query_performance_data(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            search_type=search_type,
            aggregation_type=aggregation_type,
            data_state=data_state,
            row_limit=row_limit,
            start_row=start_row,
            filters=filters,
            account=account,
        )
        return {"ok": True, **result}
    except Exception as exc:
        raise _tool_error(exc) from None


@_read_only_tool("Find top search queries")
def get_top_queries(
    start_date: str,
    end_date: str,
    site_url: str | None = None,
    search_type: str = "web",
    data_state: str | None = None,
    row_limit: int = 1000,
    start_row: int = 0,
    filters: list[dict[str, str]] | None = None,
    account: str | None = None,
) -> dict[str, Any]:
    """Get top query rows for a property over a date range."""
    try:
        result = get_top_queries_data(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            search_type=search_type,
            data_state=data_state,
            row_limit=row_limit,
            start_row=start_row,
            filters=filters,
            account=account,
        )
        return {"ok": True, **result}
    except Exception as exc:
        raise _tool_error(exc) from None


@_read_only_tool("Find top pages")
def get_top_pages(
    start_date: str,
    end_date: str,
    site_url: str | None = None,
    search_type: str = "web",
    data_state: str | None = None,
    row_limit: int = 1000,
    start_row: int = 0,
    filters: list[dict[str, str]] | None = None,
    account: str | None = None,
) -> dict[str, Any]:
    """Get top page rows for a property over a date range."""
    try:
        result = get_top_pages_data(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            search_type=search_type,
            data_state=data_state,
            row_limit=row_limit,
            start_row=start_row,
            filters=filters,
            account=account,
        )
        return {"ok": True, **result}
    except Exception as exc:
        raise _tool_error(exc) from None


@_read_only_tool("Break down Search Console performance")
def get_dimension_breakdown(
    start_date: str,
    end_date: str,
    dimension: str,
    site_url: str | None = None,
    search_type: str = "web",
    data_state: str | None = None,
    row_limit: int = 1000,
    start_row: int = 0,
    filters: list[dict[str, str]] | None = None,
    account: str | None = None,
) -> dict[str, Any]:
    """Get a single-dimension Search Analytics breakdown."""
    try:
        result = get_dimension_breakdown_data(
            dimension=dimension,
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            search_type=search_type,
            data_state=data_state,
            row_limit=row_limit,
            start_row=start_row,
            filters=filters,
            account=account,
        )
        return {"ok": True, **result}
    except Exception as exc:
        raise _tool_error(exc) from None


@_read_only_tool("Inspect URL indexing status")
def inspect_url(
    inspection_url: str,
    site_url: str | None = None,
    language_code: str | None = None,
    account: str | None = None,
) -> dict[str, Any]:
    """Read Google's indexed status for a URL within an accessible property; does not request indexing."""
    try:
        result = inspect_url_data(
            site_url=site_url,
            inspection_url=inspection_url,
            language_code=language_code,
            account=account,
        )
        return {"ok": True, **result}
    except Exception as exc:
        raise _tool_error(exc) from None


def main() -> None:
    mcp.run()
