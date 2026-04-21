# Google Search Console MCP Design

## Goal

Build a read-only MCP server for Google Search Console that mirrors the ergonomics and repository structure of `flin-google-ads-mcp`, while replacing manual refresh-token configuration with a Claude Desktop-friendly installed-app OAuth flow that stores and refreshes tokens locally.

## Product Scope

### In scope

- Read-only Search Console access
- Installed-app OAuth using the system browser and a local loopback callback
- Local token persistence and automatic access-token refresh
- Read-only site discovery helper
- Search Analytics performance querying
- URL Inspection querying
- MCP-friendly payloads optimized for Claude
- Source and published-package usage via `uv` / `uvx`
- Unit tests and documentation

### Out of scope

- Any write operation
- Sitemaps management
- Property creation or removal
- Headless auth flows without a browser
- Background caching or data warehousing
- CI live API tests

## Constraints

- Keep the repository layout and operating model close to `flin-google-ads-mcp`
- Do not require a refresh token in the Claude Desktop MCP config
- Support the initial login and re-login flow entirely from the running MCP process
- Use official Google OAuth and auth libraries for token handling
- Keep the MCP read-only by design

## Recommended Architecture

Use a hybrid architecture:

- `FastMCP` as the MCP server layer
- An explicit Search Console domain layer for API calls and payload shaping
- Google auth libraries for OAuth token acquisition, refresh, and storage

This keeps the server behavior predictable and close to the Google Ads MCP, while avoiding unnecessary custom OAuth logic.

## Repository Structure

- `src/flin_google_search_console_mcp/__init__.py`
- `src/flin_google_search_console_mcp/config.py`
- `src/flin_google_search_console_mcp/auth.py`
- `src/flin_google_search_console_mcp/search_console.py`
- `src/flin_google_search_console_mcp/server.py`
- `tests/conftest.py`
- `tests/test_config.py`
- `tests/test_auth.py`
- `tests/test_search_console.py`
- `tests/test_server_tools.py`
- `docs/mcp-usage-guide.md`
- `docs/testing.md`
- `docs/release.md`

## Authentication Design

### Configuration

Required environment variables:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

Optional environment variables:

- `GOOGLE_SEARCH_CONSOLE_SITE_URL`
- `GOOGLE_SEARCH_CONSOLE_TOKEN_PATH`
- `GOOGLE_SEARCH_CONSOLE_OAUTH_PORT`

### Runtime flow

1. MCP starts without requiring any refresh token in configuration.
2. On the first tool call that needs credentials, the MCP loads the token file if present.
3. If the token is valid, it is used directly.
4. If the access token is expired but the refresh token is valid, credentials refresh automatically.
5. If no token file exists, the refresh token is missing, revoked, or invalid, the MCP starts the installed-app OAuth flow in the system browser.
6. The loopback callback completes locally, and the resulting credentials are written to the token file.

### Token storage

- Default token path should live in a user-scoped application data location
- The path can be overridden with `GOOGLE_SEARCH_CONSOLE_TOKEN_PATH`
- The file stores token, refresh token, client id, client secret, scopes, and expiry data through the official Google credentials serialization format

## MCP Tool Surface

### `health_check`

Purpose:

- Validate required env vars
- Report whether credentials are ready, refreshable, or require interactive auth
- Confirm default site configuration
- Optionally verify that Search Console API initialization is possible

### `list_sites`

Purpose:

- Return the Search Console properties accessible by the authenticated user
- Help Claude resolve the correct `site_url`

### `get_site_summary`

Purpose:

- Return aggregate metrics for a site and date range without dimensions

Important fields:

- `clicks`
- `impressions`
- `ctr`
- `position`

### `query_performance`

Purpose:

- Core Search Analytics entry point

Inputs:

- `site_url`
- `start_date`
- `end_date`
- `dimensions`
- `search_type`
- `aggregation_type`
- `data_state`
- `row_limit`
- `start_row`
- `filters`

Outputs:

- `items[]` containing:
  - `dimensions`
  - `metrics`
- `meta` containing:
  - `response_aggregation_type`
  - `rows_returned`
  - `row_limit`
  - `start_row`
  - incomplete-data metadata when present

### `get_top_queries`

Purpose:

- Opinionated wrapper over `query_performance` with `dimensions=["query"]`

### `get_top_pages`

Purpose:

- Opinionated wrapper over `query_performance` with `dimensions=["page"]`

### `get_dimension_breakdown`

Purpose:

- Opinionated breakdown helper for `country`, `device`, `searchAppearance`, or `date`

### `inspect_url`

Purpose:

- Run URL Inspection for a single URL under a property

Important fields:

- `verdict`
- `coverage_state`
- `page_fetch_state`
- `indexing_state`
- `robots_txt_state`
- `last_crawl_time`
- `google_canonical`
- `user_canonical`
- `crawled_as`
- `sitemaps`
- `referring_urls`
- `rich_results`
- `amp_result`

## Data Prioritization

### Tier 1

- Performance metrics: `clicks`, `impressions`, `ctr`, `position`
- Core dimensions: `query`, `page`, `date`, `device`, `country`
- URL Inspection index state fields

### Tier 2

- `searchAppearance`
- `search_type`
- `aggregation_type`
- `data_state`
- response aggregation metadata
- incomplete-date / incomplete-hour metadata
- AMP and rich-results details

### Tier 3

- Deprecated mobile usability sections
- Raw low-value passthrough fields that do not improve Claude’s reasoning

## Data Modeling

### Search Analytics rows

Google returns row dimensions in positional `keys[]` arrays. The MCP should convert these to named dictionaries keyed by the requested dimensions.

Example MCP output shape:

```json
{
  "dimensions": {
    "query": "seo agent",
    "page": "https://example.com/blog/seo-agent"
  },
  "metrics": {
    "clicks": 123,
    "impressions": 4567,
    "ctr": 0.0269,
    "position": 4.2
  }
}
```

### Inspection output

Flatten the core index-status fields into a stable top-level result object and keep optional AMP / rich-results sections nested.

## Error Handling

All tools should return a consistent MCP error payload:

```json
{
  "ok": false,
  "error": {
    "type": "ErrorType",
    "message": "Human-readable error",
    "details": {}
  }
}
```

Key error classes:

- `missing_configuration`
- `oauth_required`
- `oauth_refresh_failed`
- `permission_denied`
- `invalid_site_url`
- `quota_exceeded`
- `validation_error`

## Testing Strategy

- Unit tests for config validation and default handling
- Unit tests for OAuth token loading and refresh decision paths
- Unit tests for Search Analytics request normalization and response mapping
- Unit tests for URL Inspection mapping
- Tool-level tests for server payloads and wrapper behavior
- Manual smoke-test instructions for live OAuth and API usage

## Documentation Plan

- `README.md` for setup, local usage, package usage, and Claude Desktop integration
- `docs/mcp-usage-guide.md` for operator guidance and call ordering
- `docs/testing.md` for local tests and live smoke tests
- `docs/release.md` for tag-based release flow, mirroring the Ads MCP

## Notes From Official Docs

- Search Analytics supports `type`, `aggregationType`, `dataState`, `rowLimit`, and `startRow`
- Search Analytics responses may omit rows because the API returns top results rather than a guaranteed full export
- URL Inspection requires a property `siteUrl` and an `inspectionUrl` that belongs to that property
- Read-only OAuth scope is sufficient: `https://www.googleapis.com/auth/webmasters.readonly`
- URL Inspection and Search Analytics have distinct quota characteristics and should produce quota-oriented error messages

## Primary References

- https://developers.google.com/identity/protocols/oauth2/native-app
- https://developers.google.com/webmaster-tools/v1/searchanalytics/query
- https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect
- https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult
- https://developers.google.com/webmaster-tools/limits
