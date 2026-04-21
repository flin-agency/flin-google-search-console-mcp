from __future__ import annotations

from types import SimpleNamespace

from flin_google_search_console_mcp import server


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
        lambda settings=None: {
            "status": "ready",
            "token_path": "/tmp/token.json",
            "has_token_file": True,
        },
    )

    result = server.health_check()

    assert result["ok"] is True
    assert result["status"] == "ready"
    assert result["default_site_url"] == "sc-domain:example.com"
    assert result["token_path"] == "/tmp/token.json"


def test_list_sites_returns_wrapped_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        server,
        "list_sites_data",
        lambda: {
            "count": 1,
            "items": [
                {
                    "site_url": "sc-domain:example.com",
                    "permission_level": "siteOwner",
                }
            ],
        },
    )

    result = server.list_sites()

    assert result["ok"] is True
    assert result["count"] == 1
    assert result["items"][0]["site_url"] == "sc-domain:example.com"


def test_get_site_summary_returns_wrapped_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        server,
        "get_site_summary_data",
        lambda **kwargs: {
            "site_url": "sc-domain:example.com",
            "metrics": {
                "clicks": 10,
                "impressions": 100,
                "ctr": 0.1,
                "position": 2.5,
            },
            "meta": {"response_aggregation_type": "byProperty"},
        },
    )

    result = server.get_site_summary(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
    )

    assert result["ok"] is True
    assert result["metrics"]["clicks"] == 10


def test_query_performance_returns_wrapped_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        server,
        "query_performance_data",
        lambda **kwargs: {
            "site_url": "sc-domain:example.com",
            "items": [
                {
                    "dimensions": {"query": "seo agent"},
                    "metrics": {"clicks": 5, "impressions": 50, "ctr": 0.1, "position": 3.4},
                }
            ],
            "meta": {"rows_returned": 1},
        },
    )

    result = server.query_performance(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
        dimensions=["query"],
    )

    assert result["ok"] is True
    assert result["meta"]["rows_returned"] == 1


def test_get_top_queries_returns_wrapped_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        server,
        "get_top_queries_data",
        lambda **kwargs: {
            "site_url": "sc-domain:example.com",
            "dimensions": ["query"],
            "items": [],
            "meta": {"rows_returned": 0},
        },
    )

    result = server.get_top_queries(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
    )

    assert result["ok"] is True
    assert result["dimensions"] == ["query"]


def test_get_top_pages_returns_wrapped_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        server,
        "get_top_pages_data",
        lambda **kwargs: {
            "site_url": "sc-domain:example.com",
            "dimensions": ["page"],
            "items": [],
            "meta": {"rows_returned": 0},
        },
    )

    result = server.get_top_pages(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
    )

    assert result["ok"] is True
    assert result["dimensions"] == ["page"]


def test_get_dimension_breakdown_returns_wrapped_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        server,
        "get_dimension_breakdown_data",
        lambda **kwargs: {
            "site_url": "sc-domain:example.com",
            "dimensions": ["device"],
            "items": [],
            "meta": {"rows_returned": 0},
        },
    )

    result = server.get_dimension_breakdown(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
        dimension="device",
    )

    assert result["ok"] is True
    assert result["dimensions"] == ["device"]


def test_inspect_url_returns_wrapped_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        server,
        "inspect_url_data",
        lambda **kwargs: {
            "site_url": "sc-domain:example.com",
            "inspection_url": "https://example.com/page",
            "result": {"verdict": "PASS"},
        },
    )

    result = server.inspect_url(
        site_url="sc-domain:example.com",
        inspection_url="https://example.com/page",
    )

    assert result["ok"] is True
    assert result["result"]["verdict"] == "PASS"
