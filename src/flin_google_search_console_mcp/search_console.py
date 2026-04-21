from __future__ import annotations

from datetime import date
from typing import Any, Mapping, Sequence

from .auth import get_credentials
from .config import ConfigurationError, Settings, load_settings


ALLOWED_DIMENSIONS = {
    "country",
    "date",
    "device",
    "hour",
    "page",
    "query",
    "searchAppearance",
}

ALLOWED_SEARCH_TYPES = {
    "discover",
    "googleNews",
    "image",
    "news",
    "video",
    "web",
}

SEARCH_TYPE_ALIASES = {
    "discover": "discover",
    "googlenews": "googleNews",
    "image": "image",
    "news": "news",
    "video": "video",
    "web": "web",
}

ALLOWED_AGGREGATION_TYPES = {
    "auto",
    "byNewsShowcasePanel",
    "byPage",
    "byProperty",
}

AGGREGATION_TYPE_ALIASES = {
    "auto": "auto",
    "bynewsshowcasepanel": "byNewsShowcasePanel",
    "bypage": "byPage",
    "byproperty": "byProperty",
}

ALLOWED_DATA_STATES = {
    "all",
    "final",
    "hourly_all",
}

ALLOWED_FILTER_OPERATORS = {
    "contains",
    "equals",
    "excludingRegex",
    "includingRegex",
    "notContains",
    "notEquals",
}

FILTER_OPERATOR_ALIASES = {
    operator.lower(): operator for operator in ALLOWED_FILTER_OPERATORS
}


def _to_int(value: Any) -> int:
    if value is None:
        return 0
    return int(value)


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def normalize_iso_date(raw_date: str) -> str:
    candidate = raw_date.strip()
    try:
        parsed = date.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(
            f"Invalid date {raw_date!r}. Expected format YYYY-MM-DD."
        ) from exc
    return parsed.isoformat()


def normalize_dimensions(dimensions: Sequence[str] | None) -> list[str]:
    if not dimensions:
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for raw_dimension in dimensions:
        dimension = raw_dimension.strip()
        if dimension not in ALLOWED_DIMENSIONS:
            allowed = ", ".join(sorted(ALLOWED_DIMENSIONS))
            raise ValueError(
                f"Invalid dimension {raw_dimension!r}. Allowed values: {allowed}."
            )
        if dimension in seen:
            raise ValueError(f"Duplicate dimension {dimension!r} is not allowed.")
        seen.add(dimension)
        normalized.append(dimension)
    return normalized


def normalize_search_type(search_type: str | None) -> str:
    if search_type is None:
        return "web"

    normalized = SEARCH_TYPE_ALIASES.get(search_type.strip().lower())
    if normalized is None:
        allowed = ", ".join(sorted(ALLOWED_SEARCH_TYPES))
        raise ValueError(
            f"Invalid search_type {search_type!r}. Allowed values: {allowed}."
        )
    return normalized


def normalize_aggregation_type(aggregation_type: str | None) -> str | None:
    if aggregation_type is None:
        return None

    normalized = AGGREGATION_TYPE_ALIASES.get(aggregation_type.strip().lower())
    if normalized is None:
        allowed = ", ".join(sorted(ALLOWED_AGGREGATION_TYPES))
        raise ValueError(
            f"Invalid aggregation_type {aggregation_type!r}. Allowed values: {allowed}."
        )
    return normalized


def normalize_data_state(data_state: str | None) -> str | None:
    if data_state is None:
        return None

    normalized = data_state.strip().lower()
    if normalized not in ALLOWED_DATA_STATES:
        allowed = ", ".join(sorted(ALLOWED_DATA_STATES))
        raise ValueError(
            f"Invalid data_state {data_state!r}. Allowed values: {allowed}."
        )
    return normalized


def normalize_filters(
    filters: Sequence[Mapping[str, str]] | None,
) -> list[dict[str, Any]]:
    if not filters:
        return []

    normalized_filters: list[dict[str, str]] = []
    for raw_filter in filters:
        dimension = raw_filter.get("dimension", "").strip()
        if dimension not in ALLOWED_DIMENSIONS:
            allowed = ", ".join(sorted(ALLOWED_DIMENSIONS))
            raise ValueError(
                f"Invalid filter dimension {dimension!r}. Allowed values: {allowed}."
            )

        expression = raw_filter.get("expression", "").strip()
        if not expression:
            raise ValueError("Each filter requires a non-empty expression.")

        operator = raw_filter.get("operator", "equals").strip()
        normalized_operator = FILTER_OPERATOR_ALIASES.get(operator.lower())
        if normalized_operator is None:
            allowed = ", ".join(sorted(ALLOWED_FILTER_OPERATORS))
            raise ValueError(
                f"Invalid filter operator {operator!r}. Allowed values: {allowed}."
            )

        normalized_filters.append(
            {
                "dimension": dimension,
                "operator": normalized_operator,
                "expression": expression,
            }
        )

    return [{"groupType": "and", "filters": normalized_filters}]


def clamp_row_limit(row_limit: int | None) -> int:
    if row_limit is None or row_limit <= 0:
        return 1000
    return min(row_limit, 25_000)


def normalize_start_row(start_row: int | None) -> int:
    if start_row is None:
        return 0
    if start_row < 0:
        raise ValueError("start_row must be a non-negative integer.")
    return start_row


def resolve_site_url(site_url: str | None, settings: Settings) -> str:
    candidate = site_url or settings.default_site_url
    if not candidate:
        raise ConfigurationError(
            "No site_url provided. Set GOOGLE_SEARCH_CONSOLE_SITE_URL or pass site_url to the tool."
        )
    normalized = candidate.strip()
    if not normalized:
        raise ValueError("site_url must not be empty.")
    return normalized


def _resolve_site_url_for_request(
    *, site_url: str | None, settings: Settings | None
) -> str:
    if site_url is not None:
        normalized = site_url.strip()
        if not normalized:
            raise ValueError("site_url must not be empty.")
        return normalized

    if settings is None:
        settings = load_settings()

    return resolve_site_url(site_url, settings)


def build_search_analytics_request(
    *,
    start_date: str,
    end_date: str,
    dimensions: Sequence[str] | None = None,
    search_type: str | None = None,
    aggregation_type: str | None = None,
    data_state: str | None = None,
    row_limit: int | None = None,
    start_row: int | None = None,
    filters: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, Any]:
    normalized_start = normalize_iso_date(start_date)
    normalized_end = normalize_iso_date(end_date)
    if normalized_start > normalized_end:
        raise ValueError("start_date must be less than or equal to end_date.")

    request: dict[str, Any] = {
        "startDate": normalized_start,
        "endDate": normalized_end,
        "dimensions": normalize_dimensions(dimensions),
    }

    normalized_search_type = normalize_search_type(search_type)
    if normalized_search_type:
        request["type"] = normalized_search_type

    normalized_aggregation_type = normalize_aggregation_type(aggregation_type)
    if normalized_aggregation_type:
        request["aggregationType"] = normalized_aggregation_type

    normalized_data_state = normalize_data_state(data_state)
    if normalized_data_state:
        request["dataState"] = normalized_data_state

    request["rowLimit"] = clamp_row_limit(row_limit)
    request["startRow"] = normalize_start_row(start_row)

    normalized_filter_groups = normalize_filters(filters)
    if normalized_filter_groups:
        request["dimensionFilterGroups"] = normalized_filter_groups

    return request


def map_search_analytics_response(
    *,
    response: Mapping[str, Any],
    dimensions: Sequence[str],
    row_limit: int,
    start_row: int,
) -> dict[str, Any]:
    normalized_dimensions = list(dimensions)
    rows = response.get("rows", []) or []
    items = []

    for row in rows:
        keys = list(row.get("keys", []) or [])
        named_dimensions = {
            dimension: str(keys[index])
            for index, dimension in enumerate(normalized_dimensions)
            if index < len(keys)
        }
        items.append(
            {
                "dimensions": named_dimensions,
                "metrics": {
                    "clicks": _to_int(row.get("clicks")),
                    "impressions": _to_int(row.get("impressions")),
                    "ctr": _to_float(row.get("ctr")),
                    "position": _to_float(row.get("position")),
                },
            }
        )

    meta = {
        "response_aggregation_type": response.get("responseAggregationType"),
        "rows_returned": len(items),
        "row_limit": row_limit,
        "start_row": start_row,
    }
    metadata = response.get("metadata") or {}
    if "first_incomplete_date" in metadata:
        meta["first_incomplete_date"] = metadata["first_incomplete_date"]
    if "first_incomplete_hour" in metadata:
        meta["first_incomplete_hour"] = metadata["first_incomplete_hour"]

    return {
        "items": items,
        "meta": meta,
    }


def get_search_console_service(*, credentials: Any | None = None) -> Any:
    resolved_credentials = credentials or get_credentials()

    try:
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise ConfigurationError(
            "google-api-python-client is not installed. Install project dependencies first."
        ) from exc

    return build(
        "searchconsole",
        "v1",
        credentials=resolved_credentials,
        cache_discovery=False,
    )


def list_sites(*, service: Any | None = None, credentials: Any | None = None) -> dict[str, Any]:
    resolved_service = service or get_search_console_service(credentials=credentials)
    response = resolved_service.sites().list().execute()
    entries = response.get("siteEntry", []) or []

    items = [
        {
            "site_url": str(entry.get("siteUrl", "")),
            "permission_level": str(entry.get("permissionLevel", "")),
        }
        for entry in entries
    ]
    items.sort(key=lambda item: item["site_url"])

    return {
        "count": len(items),
        "items": items,
    }


def query_performance(
    *,
    site_url: str | None = None,
    start_date: str,
    end_date: str,
    dimensions: Sequence[str] | None = None,
    search_type: str | None = None,
    aggregation_type: str | None = None,
    data_state: str | None = None,
    row_limit: int | None = None,
    start_row: int | None = None,
    filters: Sequence[Mapping[str, str]] | None = None,
    service: Any | None = None,
    credentials: Any | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    resolved_site_url = _resolve_site_url_for_request(
        site_url=site_url,
        settings=settings,
    )
    request = build_search_analytics_request(
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

    resolved_service = service or get_search_console_service(credentials=credentials)
    response = (
        resolved_service.searchanalytics()
        .query(siteUrl=resolved_site_url, body=request)
        .execute()
    )

    normalized_dimensions = request["dimensions"]
    normalized_row_limit = int(request["rowLimit"])
    normalized_start_row = int(request["startRow"])
    mapped = map_search_analytics_response(
        response=response,
        dimensions=normalized_dimensions,
        row_limit=normalized_row_limit,
        start_row=normalized_start_row,
    )

    return {
        "site_url": resolved_site_url,
        "start_date": request["startDate"],
        "end_date": request["endDate"],
        "dimensions": normalized_dimensions,
        "search_type": request.get("type", "web"),
        "aggregation_type": request.get("aggregationType"),
        "data_state": request.get("dataState"),
        "items": mapped["items"],
        "meta": mapped["meta"],
    }


def get_site_summary(
    *,
    site_url: str | None = None,
    start_date: str,
    end_date: str,
    search_type: str | None = None,
    data_state: str | None = None,
    service: Any | None = None,
    credentials: Any | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    result = query_performance(
        site_url=site_url,
        start_date=start_date,
        end_date=end_date,
        dimensions=[],
        search_type=search_type,
        data_state=data_state,
        row_limit=1,
        start_row=0,
        service=service,
        credentials=credentials,
        settings=settings,
    )

    metrics = (
        result["items"][0]["metrics"]
        if result["items"]
        else {"clicks": 0, "impressions": 0, "ctr": 0.0, "position": 0.0}
    )

    return {
        "site_url": result["site_url"],
        "start_date": result["start_date"],
        "end_date": result["end_date"],
        "search_type": result["search_type"],
        "metrics": metrics,
        "meta": result["meta"],
    }


def get_top_queries(**kwargs: Any) -> dict[str, Any]:
    return query_performance(dimensions=["query"], **kwargs)


def get_top_pages(**kwargs: Any) -> dict[str, Any]:
    return query_performance(dimensions=["page"], **kwargs)


def get_dimension_breakdown(*, dimension: str, **kwargs: Any) -> dict[str, Any]:
    normalized_dimension = normalize_dimensions([dimension])[0]
    return query_performance(dimensions=[normalized_dimension], **kwargs)


def map_url_inspection_result(result: Mapping[str, Any]) -> dict[str, Any]:
    index_status = result.get("indexStatusResult") or {}

    return {
        "inspection_result_link": result.get("inspectionResultLink"),
        "verdict": index_status.get("verdict"),
        "coverage_state": index_status.get("coverageState"),
        "robots_txt_state": index_status.get("robotsTxtState"),
        "indexing_state": index_status.get("indexingState"),
        "last_crawl_time": index_status.get("lastCrawlTime"),
        "page_fetch_state": index_status.get("pageFetchState"),
        "google_canonical": index_status.get("googleCanonical"),
        "user_canonical": index_status.get("userCanonical"),
        "crawled_as": index_status.get("crawledAs"),
        "sitemaps": list(index_status.get("sitemap", []) or []),
        "referring_urls": list(index_status.get("referringUrls", []) or []),
        "amp_result": result.get("ampResult"),
        "rich_results": result.get("richResultsResult"),
        "mobile_usability_result": result.get("mobileUsabilityResult"),
    }


def inspect_url(
    *,
    site_url: str | None = None,
    inspection_url: str,
    language_code: str | None = None,
    service: Any | None = None,
    credentials: Any | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    resolved_site_url = _resolve_site_url_for_request(
        site_url=site_url,
        settings=settings,
    )
    request_body: dict[str, Any] = {
        "inspectionUrl": inspection_url.strip(),
        "siteUrl": resolved_site_url,
    }
    if not request_body["inspectionUrl"]:
        raise ValueError("inspection_url must not be empty.")
    if language_code and language_code.strip():
        request_body["languageCode"] = language_code.strip()

    resolved_service = service or get_search_console_service(credentials=credentials)
    response = (
        resolved_service.urlInspection()
        .index()
        .inspect(body=request_body)
        .execute()
    )
    inspection_result = response.get("inspectionResult", {}) or {}

    return {
        "site_url": resolved_site_url,
        "inspection_url": request_body["inspectionUrl"],
        "language_code": request_body.get("languageCode"),
        "result": map_url_inspection_result(inspection_result),
    }
