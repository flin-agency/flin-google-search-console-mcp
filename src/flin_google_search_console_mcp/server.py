from __future__ import annotations

from typing import Any, Sequence

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    class FastMCP:  # type: ignore[override]
        def __init__(self, name: str, instructions: str) -> None:
            self.name = name
            self.instructions = instructions

        def tool(self):
            def decorator(func):
                return func

            return decorator

        def run(self) -> None:
            raise RuntimeError(
                "mcp dependency is not installed. Install project dependencies first."
            )

from .auth import describe_auth_state
from .config import load_settings, missing_required_env_vars
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


def _error_payload(exc: Exception) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "type": exc.__class__.__name__,
            "message": str(exc),
        },
    }


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Check configuration and authentication readiness for Google Search Console."""
    missing = missing_required_env_vars()
    if missing:
        return {
            "ok": False,
            "status": "missing_configuration",
            "missing_env_vars": missing,
        }

    try:
        settings = load_settings()
        auth_state = describe_auth_state(settings=settings)
    except Exception as exc:
        return _error_payload(exc)

    return {
        "ok": auth_state["status"] in {"ready", "refreshable"},
        "status": auth_state["status"],
        "default_site_url": settings.default_site_url,
        "has_token_file": auth_state["has_token_file"],
        "oauth_port": settings.oauth_port,
    }


@mcp.tool()
def list_sites() -> dict[str, Any]:
    """List Search Console properties accessible by the authenticated user."""
    try:
        result = list_sites_data()
        return {"ok": True, **result}
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def get_site_summary(
    start_date: str,
    end_date: str,
    site_url: str | None = None,
    search_type: str = "web",
    data_state: str | None = None,
) -> dict[str, Any]:
    """Get aggregate performance metrics for a property over a date range."""
    try:
        result = get_site_summary_data(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            search_type=search_type,
            data_state=data_state,
        )
        return {"ok": True, **result}
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
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
        )
        return {"ok": True, **result}
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def get_top_queries(
    start_date: str,
    end_date: str,
    site_url: str | None = None,
    search_type: str = "web",
    data_state: str | None = None,
    row_limit: int = 1000,
    start_row: int = 0,
    filters: list[dict[str, str]] | None = None,
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
        )
        return {"ok": True, **result}
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def get_top_pages(
    start_date: str,
    end_date: str,
    site_url: str | None = None,
    search_type: str = "web",
    data_state: str | None = None,
    row_limit: int = 1000,
    start_row: int = 0,
    filters: list[dict[str, str]] | None = None,
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
        )
        return {"ok": True, **result}
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
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
        )
        return {"ok": True, **result}
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def inspect_url(
    inspection_url: str,
    site_url: str | None = None,
    language_code: str | None = None,
) -> dict[str, Any]:
    """Inspect the indexed status of a specific URL under a property."""
    try:
        result = inspect_url_data(
            site_url=site_url,
            inspection_url=inspection_url,
            language_code=language_code,
        )
        return {"ok": True, **result}
    except Exception as exc:
        return _error_payload(exc)


def main() -> None:
    mcp.run()
