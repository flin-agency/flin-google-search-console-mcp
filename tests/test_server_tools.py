from __future__ import annotations

from types import SimpleNamespace
import asyncio

from googleapiclient.errors import HttpError
from httplib2 import Response
from mcp.shared.memory import create_connected_server_and_client_session
import pytest

from flin_google_search_console_mcp import server


def test_mcp_advertises_read_only_annotations() -> None:
    async def list_tools():
        async with create_connected_server_and_client_session(server.mcp) as client:
            response = await client.list_tools()
            assert len(response.tools) == 8
            for tool in response.tools:
                assert tool.annotations is not None
                assert tool.annotations.title
                assert tool.annotations.readOnlyHint is True
                assert tool.annotations.destructiveHint is False
                assert tool.annotations.idempotentHint is True
                assert tool.annotations.openWorldHint is (tool.name != "health_check")

    asyncio.run(list_tools())


@pytest.mark.parametrize(
    ("tool_name", "backend_name", "arguments"),
    [
        ("health_check", "load_settings", {}),
        ("list_sites", "list_sites_data", {}),
        ("get_site_summary", "get_site_summary_data", {"start_date": "2026-04-01", "end_date": "2026-04-10"}),
        ("query_performance", "query_performance_data", {"start_date": "2026-04-01", "end_date": "2026-04-10"}),
        ("get_top_queries", "get_top_queries_data", {"start_date": "2026-04-01", "end_date": "2026-04-10"}),
        ("get_top_pages", "get_top_pages_data", {"start_date": "2026-04-01", "end_date": "2026-04-10"}),
        ("get_dimension_breakdown", "get_dimension_breakdown_data", {"start_date": "2026-04-01", "end_date": "2026-04-10", "dimension": "device"}),
        ("inspect_url", "inspect_url_data", {"inspection_url": "https://example.com/"}),
    ],
)
def test_all_tools_raise_sanitized_errors(monkeypatch, tool_name, backend_name, arguments) -> None:
    def fail(**kwargs):
        raise PermissionError(13, "private details", "/private/user/token.json")

    monkeypatch.setattr(server, "missing_required_env_vars", lambda: [])
    monkeypatch.setattr(server, backend_name, fail)

    with pytest.raises(server.ToolError, match="io_error") as error:
        getattr(server, tool_name)(**arguments)

    assert "private" not in str(error.value)
    assert "token.json" not in str(error.value)


@pytest.mark.parametrize(
    ("error", "code"),
    [
        (server.ConfigurationError("sensitive-marker"), "invalid_configuration"),
        (server.AuthenticationRequiredError("sensitive-marker"), "oauth_required"),
        (server.AuthenticationError("sensitive-marker"), "authentication_failed"),
        (ValueError("sensitive-marker"), "invalid_arguments"),
        (TimeoutError("sensitive-marker"), "request_timeout"),
        (RuntimeError("sensitive-marker"), "internal_error"),
    ] + [
        (HttpError(
            Response({"status": str(status)}),
            b'{"error":{"message":"sensitive-marker"}}',
            uri="https://example.com/private?access_token=sensitive-marker",
        ), code)
        for status, code in [
            (400, "google_request_failed"), (401, "oauth_required"),
            (403, "permission_denied"), (429, "quota_exceeded"),
            (503, "service_unavailable"),
        ]
    ],
)
def test_mcp_reports_sanitized_failures_as_errors(monkeypatch, caplog, error, code) -> None:
    def fail(**kwargs):
        raise error

    monkeypatch.setattr(server, "list_sites_data", fail)

    async def call_tool():
        async with create_connected_server_and_client_session(server.mcp) as client:
            result = await client.call_tool("list_sites", {})
            assert result.isError is True
            assert code in result.content[0].text
            assert "sensitive-marker" not in result.model_dump_json()

    asyncio.run(call_tool())
    assert "sensitive-marker" not in caplog.text


def test_mcp_preserves_successful_results_and_health_diagnostics(monkeypatch) -> None:
    monkeypatch.setattr(server, "list_sites_data", lambda **kwargs: {"count": 0, "items": []})
    monkeypatch.setattr(server, "missing_required_env_vars", lambda: ["GOOGLE_CLIENT_ID"])

    async def call_tools():
        async with create_connected_server_and_client_session(server.mcp) as client:
            result = await client.call_tool("list_sites", {})
            assert result.isError is False
            assert result.structuredContent == {"ok": True, "count": 0, "items": []}
            health = await client.call_tool("health_check", {})
            assert health.isError is False
            assert health.structuredContent["status"] == "missing_configuration"

    asyncio.run(call_tools())


def test_health_check_reports_missing_configuration(monkeypatch) -> None:
    monkeypatch.setattr(
        server,
        "missing_required_env_vars",
        lambda env=None: ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"],
    )

    result = server.health_check()

    assert result == {
        "ok": False,
        "status": "missing_configuration",
        "server_version": server.__version__,
        "missing_env_vars": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"],
    }


def test_health_check_reports_ready_state(monkeypatch) -> None:
    monkeypatch.setattr(server, "missing_required_env_vars", lambda env=None: [])
    monkeypatch.setattr(
        server,
        "load_settings",
        lambda: SimpleNamespace(
            default_site_url="sc-domain:example.com",
            token_path="/tmp/token.json",
            oauth_port=0,
        ),
    )
    monkeypatch.setattr(
        server,
        "describe_auth_state",
        lambda settings=None, account=None: {
            "status": "ready",
            "token_path": "/tmp/token.json",
            "has_token_file": True,
        },
    )

    result = server.health_check()

    assert result["ok"] is True
    assert result["status"] == "ready"
    assert result["default_site_url"] == "sc-domain:example.com"
    assert "token_path" not in result


def test_health_check_uses_named_account(monkeypatch) -> None:
    captured = {}
    monkeypatch.setattr(server, "missing_required_env_vars", lambda env=None: [])
    monkeypatch.setattr(
        server,
        "load_settings",
        lambda: SimpleNamespace(
            default_site_url="sc-domain:example.com",
            token_path="/tmp/token.json",
            token_dir="/tmp",
            oauth_port=0,
        ),
    )

    def fake_describe_auth_state(settings=None, account=None):
        captured["account"] = account
        return {
            "status": "ready",
            "has_token_file": True,
        }

    monkeypatch.setattr(server, "describe_auth_state", fake_describe_auth_state)

    result = server.health_check(account="work")

    assert result["ok"] is True
    assert result["account"] == "work"
    assert captured["account"] == "work"


def test_list_sites_returns_wrapped_payload(monkeypatch) -> None:
    captured = {}

    def fake_list_sites_data(account=None):
        captured["account"] = account
        return {
            "account": account,
            "count": 1,
            "items": [
                {
                    "site_url": "sc-domain:example.com",
                    "permission_level": "siteOwner",
                }
            ],
        }

    monkeypatch.setattr(
        server,
        "list_sites_data",
        fake_list_sites_data,
    )

    result = server.list_sites(account="work")

    assert result["ok"] is True
    assert result["account"] == "work"
    assert captured["account"] == "work"
    assert result["count"] == 1
    assert result["items"][0]["site_url"] == "sc-domain:example.com"


def test_get_site_summary_returns_wrapped_payload(monkeypatch) -> None:
    captured = {}

    def fake_get_site_summary_data(**kwargs):
        captured.update(kwargs)
        return {
            "site_url": "sc-domain:example.com",
            "metrics": {
                "clicks": 10,
                "impressions": 100,
                "ctr": 0.1,
                "position": 2.5,
            },
            "meta": {"response_aggregation_type": "byProperty"},
        }

    monkeypatch.setattr(
        server,
        "get_site_summary_data",
        fake_get_site_summary_data,
    )

    result = server.get_site_summary(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
        account="work",
    )

    assert result["ok"] is True
    assert result["metrics"]["clicks"] == 10
    assert captured["account"] == "work"


def test_query_performance_returns_wrapped_payload(monkeypatch) -> None:
    captured = {}

    def fake_query_performance_data(**kwargs):
        captured.update(kwargs)
        return {
            "site_url": "sc-domain:example.com",
            "items": [
                {
                    "dimensions": {"query": "seo agent"},
                    "metrics": {"clicks": 5, "impressions": 50, "ctr": 0.1, "position": 3.4},
                }
            ],
            "meta": {"rows_returned": 1},
        }

    monkeypatch.setattr(
        server,
        "query_performance_data",
        fake_query_performance_data,
    )

    result = server.query_performance(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
        dimensions=["query"],
        account="work",
    )

    assert result["ok"] is True
    assert result["meta"]["rows_returned"] == 1
    assert captured["account"] == "work"


def test_get_top_queries_returns_wrapped_payload(monkeypatch) -> None:
    captured = {}

    def fake_get_top_queries_data(**kwargs):
        captured.update(kwargs)
        return {
            "site_url": "sc-domain:example.com",
            "dimensions": ["query"],
            "items": [],
            "meta": {"rows_returned": 0},
        }

    monkeypatch.setattr(
        server,
        "get_top_queries_data",
        fake_get_top_queries_data,
    )

    result = server.get_top_queries(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
        account="work",
    )

    assert result["ok"] is True
    assert result["dimensions"] == ["query"]
    assert captured["account"] == "work"


def test_get_top_pages_returns_wrapped_payload(monkeypatch) -> None:
    captured = {}

    def fake_get_top_pages_data(**kwargs):
        captured.update(kwargs)
        return {
            "site_url": "sc-domain:example.com",
            "dimensions": ["page"],
            "items": [],
            "meta": {"rows_returned": 0},
        }

    monkeypatch.setattr(
        server,
        "get_top_pages_data",
        fake_get_top_pages_data,
    )

    result = server.get_top_pages(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
        account="work",
    )

    assert result["ok"] is True
    assert result["dimensions"] == ["page"]
    assert captured["account"] == "work"


def test_get_dimension_breakdown_returns_wrapped_payload(monkeypatch) -> None:
    captured = {}

    def fake_get_dimension_breakdown_data(**kwargs):
        captured.update(kwargs)
        return {
            "site_url": "sc-domain:example.com",
            "dimensions": ["device"],
            "items": [],
            "meta": {"rows_returned": 0},
        }

    monkeypatch.setattr(
        server,
        "get_dimension_breakdown_data",
        fake_get_dimension_breakdown_data,
    )

    result = server.get_dimension_breakdown(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
        dimension="device",
        account="work",
    )

    assert result["ok"] is True
    assert result["dimensions"] == ["device"]
    assert captured["account"] == "work"


def test_inspect_url_returns_wrapped_payload(monkeypatch) -> None:
    captured = {}

    def fake_inspect_url_data(**kwargs):
        captured.update(kwargs)
        return {
            "site_url": "sc-domain:example.com",
            "inspection_url": "https://example.com/page",
            "result": {"verdict": "PASS"},
        }

    monkeypatch.setattr(
        server,
        "inspect_url_data",
        fake_inspect_url_data,
    )

    result = server.inspect_url(
        site_url="sc-domain:example.com",
        inspection_url="https://example.com/page",
        account="work",
    )

    assert result["ok"] is True
    assert result["result"]["verdict"] == "PASS"
    assert captured["account"] == "work"
