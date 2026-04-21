# flin-google-search-console-mcp

Read-only MCP server for Google Search Console, built for simple public use via `uvx`.

## Why this server

- Read-only by design
- No sitemap submit or other write operations
- Similar structure and ergonomics to `flin-google-ads-mcp`
- No refresh token required in Claude Desktop config
- Local token storage with automatic refresh after first browser login
- Optimized for Search Console performance analysis and URL inspection

## Exposed MCP tools

- `health_check`
- `list_sites`
- `get_site_summary`
- `query_performance`
- `get_top_queries`
- `get_top_pages`
- `get_dimension_breakdown`
- `inspect_url`

## What the MCP stores locally

The MCP uses the Google installed-app OAuth flow:

1. Claude Desktop starts the MCP
2. The first auth-required tool call opens a browser window
3. You log into Google and grant Search Console read-only access
4. The MCP stores the resulting token JSON locally
5. Future runs refresh the access token automatically

This means the Claude Desktop config only needs:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

Optional:

- `GOOGLE_SEARCH_CONSOLE_SITE_URL`
- `GOOGLE_SEARCH_CONSOLE_TOKEN_PATH`
- `GOOGLE_SEARCH_CONSOLE_OAUTH_PORT`

The default OAuth scope is:

- `https://www.googleapis.com/auth/webmasters.readonly`

## Requirements

1. Python 3.10+
2. Node.js v25.8.1+ for MCP Inspector testing
3. A Google Cloud OAuth Desktop App client
4. Search Console property access for the Google account used during login

## Recommended OAuth client setup

Create a Google Cloud OAuth client of type `Desktop app`, then use the generated client id and client secret.

The MCP handles:

- initial browser login
- local token persistence
- automatic access-token refresh
- re-login when the refresh token is missing, revoked, or invalid

## Quickstart (from source)

```bash
uv sync --extra dev
cp .env.example .env
# Fill .env values
uv run flin-google-search-console-mcp
```

## Quickstart (as published package)

```bash
uvx flin-google-search-console-mcp@latest
```

## Claude Desktop integration (published via uvx)

```json
{
  "mcpServers": {
    "flin-google-search-console-mcp": {
      "command": "uvx",
      "args": ["flin-google-search-console-mcp@latest"],
      "env": {
        "GOOGLE_CLIENT_ID": "xxx",
        "GOOGLE_CLIENT_SECRET": "xxx",
        "GOOGLE_SEARCH_CONSOLE_SITE_URL": "sc-domain:example.com"
      }
    }
  }
}
```

If you want the token file in a stable custom location:

```json
{
  "mcpServers": {
    "flin-google-search-console-mcp": {
      "command": "uvx",
      "args": ["flin-google-search-console-mcp@latest"],
      "env": {
        "GOOGLE_CLIENT_ID": "xxx",
        "GOOGLE_CLIENT_SECRET": "xxx",
        "GOOGLE_SEARCH_CONSOLE_SITE_URL": "sc-domain:example.com",
        "GOOGLE_SEARCH_CONSOLE_TOKEN_PATH": "/Users/you/.config/flin-google-search-console-mcp/token.json"
      }
    }
  }
}
```

## Claude Desktop integration (local development)

```json
{
  "mcpServers": {
    "flin-google-search-console-mcp-local": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/nicolasg/Antigravity/flin-google-search-console-mcp",
        "flin-google-search-console-mcp"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "xxx",
        "GOOGLE_CLIENT_SECRET": "xxx",
        "GOOGLE_SEARCH_CONSOLE_SITE_URL": "sc-domain:example.com"
      }
    }
  }
}
```

## Typical usage flow

1. Run `health_check`
2. Run `list_sites` if you are unsure which property string to use
3. Run `get_site_summary` for a quick answer
4. Run `get_top_queries` or `get_top_pages` for common investigations
5. Run `query_performance` for custom dimensions, filters, and pagination
6. Run `inspect_url` when you need indexability and canonical details for a specific URL

## Important Search Analytics notes

- `query_performance` uses Search Console Search Analytics under the hood
- Results are top rows, not guaranteed full exports
- Supported knobs include:
  - `dimensions`
  - `filters`
  - `search_type`
  - `aggregation_type`
  - `data_state`
  - `row_limit`
  - `start_row`
- The MCP maps Google `keys[]` arrays into named dimension objects to make responses easier for Claude to reason about

## Example tool calls

### Site summary

```json
{
  "tool": "get_site_summary",
  "args": {
    "site_url": "sc-domain:example.com",
    "start_date": "2026-04-01",
    "end_date": "2026-04-20"
  }
}
```

### Top queries

```json
{
  "tool": "get_top_queries",
  "args": {
    "site_url": "sc-domain:example.com",
    "start_date": "2026-04-01",
    "end_date": "2026-04-20",
    "row_limit": 25
  }
}
```

### Page breakdown with device filter

```json
{
  "tool": "query_performance",
  "args": {
    "site_url": "sc-domain:example.com",
    "start_date": "2026-04-01",
    "end_date": "2026-04-20",
    "dimensions": ["page"],
    "filters": [
      {
        "dimension": "device",
        "operator": "equals",
        "expression": "MOBILE"
      }
    ],
    "row_limit": 50
  }
}
```

### URL inspection

```json
{
  "tool": "inspect_url",
  "args": {
    "site_url": "sc-domain:example.com",
    "inspection_url": "https://example.com/blog/seo-agent"
  }
}
```

## Search types

`query_performance` and helper tools support:

- `web`
- `image`
- `video`
- `discover`
- `googleNews`
- `news`

## How to test

Detailed guide: [docs/testing.md](docs/testing.md)
- Release checklist: [docs/release.md](docs/release.md)
- Operational guide: [docs/mcp-usage-guide.md](docs/mcp-usage-guide.md)

Fast path:

```bash
uv sync --extra dev
python3 -m pytest
python3 -m compileall src
uv build
```

## Release on GitHub + PyPI

This repository publishes automatically with GitHub Actions:

- CI: `.github/workflows/ci.yml`
- Release: `.github/workflows/release.yml` triggered by git tags `v*`

### 1) Configure PyPI Trusted Publisher (one-time)

In PyPI project settings for `flin-google-search-console-mcp`, add a Trusted Publisher with:

- Owner: `flin-agency`
- Repository: `flin-google-search-console-mcp`
- Workflow: `release.yml`
- Environment: `pypi`

### 2) Cut a release

```bash
git add -A
git commit -m "release: v0.1.0"
git tag v0.1.0
git push origin main --tags
```

## CI

GitHub Actions validates:

- unit tests
- import and compile checks
- package build
