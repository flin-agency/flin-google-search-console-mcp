from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import sys
from types import ModuleType, SimpleNamespace

import pytest

from flin_google_search_console_mcp.search_console import (
    build_search_analytics_request,
    get_search_console_service,
    get_site_summary,
    map_search_analytics_response,
    map_url_inspection_result,
    normalize_dimensions,
    normalize_filters,
    normalize_search_type,
    query_performance,
)


class _ExecuteCall:
    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response

    def execute(self) -> dict[str, Any]:
        return self._response


@dataclass
class FakeSearchAnalyticsResource:
    response: dict[str, Any]
    calls: list[dict[str, Any]] = field(default_factory=list)

    def query(self, *, siteUrl: str, body: dict[str, Any]) -> _ExecuteCall:
        self.calls.append({"siteUrl": siteUrl, "body": body})
        return _ExecuteCall(self.response)


@dataclass
class FakeUrlInspectionResource:
    response: dict[str, Any]
    calls: list[dict[str, Any]] = field(default_factory=list)

    def inspect(self, *, body: dict[str, Any]) -> _ExecuteCall:
        self.calls.append(body)
        return _ExecuteCall(self.response)


class FakeUrlInspectionRoot:
    def __init__(self, resource: FakeUrlInspectionResource) -> None:
        self._resource = resource

    def index(self) -> FakeUrlInspectionResource:
        return self._resource


@dataclass
class FakeService:
    searchanalytics_resource: FakeSearchAnalyticsResource | None = None
    urlinspection_resource: FakeUrlInspectionResource | None = None

    def searchanalytics(self) -> FakeSearchAnalyticsResource:
        assert self.searchanalytics_resource is not None
        return self.searchanalytics_resource

    def urlInspection(self) -> FakeUrlInspectionRoot:
        assert self.urlinspection_resource is not None
        return FakeUrlInspectionRoot(self.urlinspection_resource)


def test_normalize_dimensions_preserves_order() -> None:
    assert normalize_dimensions(["query", "page", "device"]) == [
        "query",
        "page",
        "device",
    ]


def test_normalize_dimensions_rejects_duplicate_values() -> None:
    with pytest.raises(ValueError):
        normalize_dimensions(["query", "query"])


def test_normalize_filters_builds_dimension_filter_group() -> None:
    filters = normalize_filters(
        [
            {"dimension": "country", "operator": "equals", "expression": "CHE"},
            {"dimension": "device", "operator": "notEquals", "expression": "TABLET"},
        ]
    )

    assert filters == [
        {
            "groupType": "and",
            "filters": [
                {
                    "dimension": "country",
                    "operator": "equals",
                    "expression": "CHE",
                },
                {
                    "dimension": "device",
                    "operator": "notEquals",
                    "expression": "TABLET",
                },
            ],
        }
    ]


def test_normalize_search_type_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        normalize_search_type("shopping")


def test_build_search_analytics_request_includes_optional_fields() -> None:
    request = build_search_analytics_request(
        start_date="2026-04-01",
        end_date="2026-04-10",
        dimensions=["query", "page"],
        search_type="web",
        aggregation_type="byPage",
        data_state="all",
        row_limit=250,
        start_row=50,
        filters=[{"dimension": "country", "expression": "CHE"}],
    )

    assert request == {
        "startDate": "2026-04-01",
        "endDate": "2026-04-10",
        "dimensions": ["query", "page"],
        "type": "web",
        "aggregationType": "byPage",
        "dataState": "all",
        "rowLimit": 250,
        "startRow": 50,
        "dimensionFilterGroups": [
            {
                "groupType": "and",
                "filters": [
                    {
                        "dimension": "country",
                        "operator": "equals",
                        "expression": "CHE",
                    }
                ],
            }
        ],
    }


def test_map_search_analytics_response_uses_named_dimensions() -> None:
    response = {
        "rows": [
            {
                "keys": ["seo agent", "https://example.com/seo-agent"],
                "clicks": 12,
                "impressions": 345,
                "ctr": 0.0347,
                "position": 5.5,
            }
        ],
        "responseAggregationType": "byPage",
        "metadata": {"first_incomplete_date": "2026-04-10"},
    }

    result = map_search_analytics_response(
        response=response,
        dimensions=["query", "page"],
        row_limit=250,
        start_row=0,
    )

    assert result["items"] == [
        {
            "dimensions": {
                "query": "seo agent",
                "page": "https://example.com/seo-agent",
            },
            "metrics": {
                "clicks": 12,
                "impressions": 345,
                "ctr": 0.0347,
                "position": 5.5,
            },
        }
    ]
    assert result["meta"]["response_aggregation_type"] == "byPage"
    assert result["meta"]["first_incomplete_date"] == "2026-04-10"


def test_get_site_summary_returns_aggregate_metrics() -> None:
    resource = FakeSearchAnalyticsResource(
        response={
            "rows": [
                {
                    "clicks": 120,
                    "impressions": 4800,
                    "ctr": 0.025,
                    "position": 8.1,
                }
            ],
            "responseAggregationType": "byProperty",
        }
    )
    service = FakeService(searchanalytics_resource=resource)

    result = get_site_summary(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
        service=service,
    )

    assert result["site_url"] == "sc-domain:example.com"
    assert result["metrics"] == {
        "clicks": 120,
        "impressions": 4800,
        "ctr": 0.025,
        "position": 8.1,
    }
    assert resource.calls[0]["body"]["dimensions"] == []


def test_query_performance_calls_search_analytics_with_normalized_request() -> None:
    resource = FakeSearchAnalyticsResource(
        response={"rows": [], "responseAggregationType": "auto"}
    )
    service = FakeService(searchanalytics_resource=resource)

    query_performance(
        site_url="sc-domain:example.com",
        start_date="2026-04-01",
        end_date="2026-04-10",
        dimensions=["date"],
        search_type="web",
        row_limit=25,
        start_row=10,
        service=service,
    )

    assert resource.calls == [
        {
            "siteUrl": "sc-domain:example.com",
            "body": {
                "startDate": "2026-04-01",
                "endDate": "2026-04-10",
                "dimensions": ["date"],
                "type": "web",
                "rowLimit": 25,
                "startRow": 10,
            },
        }
    ]


def test_get_search_console_service_builds_searchconsole_v1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_build(
        service_name: str,
        version: str,
        *,
        credentials: object,
        cache_discovery: bool,
    ) -> str:
        captured["service_name"] = service_name
        captured["version"] = version
        captured["credentials"] = credentials
        captured["cache_discovery"] = cache_discovery
        return "service"

    discovery_module = ModuleType("googleapiclient.discovery")
    discovery_module.build = fake_build
    googleapiclient_module = ModuleType("googleapiclient")
    googleapiclient_module.discovery = discovery_module
    monkeypatch.setitem(sys.modules, "googleapiclient", googleapiclient_module)
    monkeypatch.setitem(sys.modules, "googleapiclient.discovery", discovery_module)

    credentials = object()
    result = get_search_console_service(credentials=credentials)

    assert result == "service"
    assert captured == {
        "service_name": "searchconsole",
        "version": "v1",
        "credentials": credentials,
        "cache_discovery": False,
    }


def test_map_url_inspection_result_flattens_core_fields() -> None:
    payload = {
        "inspectionResultLink": "https://search.google.com/test/inspection",
        "indexStatusResult": {
            "verdict": "PASS",
            "coverageState": "Submitted and indexed",
            "robotsTxtState": "ALLOWED",
            "indexingState": "INDEXING_ALLOWED",
            "lastCrawlTime": "2026-04-20T08:00:00Z",
            "pageFetchState": "SUCCESSFUL",
            "googleCanonical": "https://example.com/canonical",
            "userCanonical": "https://example.com/canonical",
            "crawledAs": "MOBILE",
            "sitemap": ["https://example.com/sitemap.xml"],
            "referringUrls": ["https://example.com/internal-link"],
        },
        "richResultsResult": {
            "verdict": "PASS",
            "detectedItems": [{"name": "BreadcrumbList", "issues": []}],
        },
    }

    result = map_url_inspection_result(payload)

    assert result["inspection_result_link"] == "https://search.google.com/test/inspection"
    assert result["verdict"] == "PASS"
    assert result["coverage_state"] == "Submitted and indexed"
    assert result["page_fetch_state"] == "SUCCESSFUL"
    assert result["sitemaps"] == ["https://example.com/sitemap.xml"]
    assert result["referring_urls"] == ["https://example.com/internal-link"]
    assert result["rich_results"]["verdict"] == "PASS"
