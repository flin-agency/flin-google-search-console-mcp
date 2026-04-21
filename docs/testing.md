# Testing Guide

This guide covers how to test `flin-google-search-console-mcp` from zero to production confidence.

## Test levels

1. Local static and unit tests
2. Local MCP runtime test with Inspector
3. End-to-end test in Claude using `uvx`
4. CI test on each push or pull request

## 1) Local static and unit tests

Run these first on every change:

```bash
uv sync --extra dev
python3 -m pytest
python3 -m compileall src
uv build
```

What this validates:

- config validation
- token-management logic
- Search Analytics request and response mapping
- server tool payloads
- Python syntax and package buildability

## 2) Local MCP runtime test with Inspector

Requires Node.js v25.8.1+.

### 2.1 Export credentials in your shell

```bash
export GOOGLE_CLIENT_ID="..."
export GOOGLE_CLIENT_SECRET="..."
export GOOGLE_SEARCH_CONSOLE_SITE_URL="sc-domain:example.com"
```

Optional:

```bash
export GOOGLE_SEARCH_CONSOLE_TOKEN_PATH="$HOME/.config/flin-google-search-console-mcp/token.json"
export GOOGLE_SEARCH_CONSOLE_OAUTH_PORT="0"
```

### 2.2 List tools

```bash
npx -y @modelcontextprotocol/inspector --cli \
  uv run flin-google-search-console-mcp \
  --method tools/list
```

Expected:

- `health_check`
- `list_sites`
- `get_site_summary`
- `query_performance`
- `get_top_queries`
- `get_top_pages`
- `get_dimension_breakdown`
- `inspect_url`

### 2.3 Health check

```bash
npx -y @modelcontextprotocol/inspector --cli \
  uv run flin-google-search-console-mcp \
  --method tools/call \
  --tool-name health_check
```

Expected on a fresh machine:

- either `status = "oauth_required"` before login
- or `status = "ready"` after login

### 2.4 Complete the interactive login

Run a tool that requires Search Console access, for example:

```bash
npx -y @modelcontextprotocol/inspector --cli \
  uv run flin-google-search-console-mcp \
  --method tools/call \
  --tool-name list_sites
```

Expected:

- A browser window opens
- You complete Google login and consent
- The MCP writes a local token file

### 2.5 Smoke-test the main tools

Site summary:

```bash
npx -y @modelcontextprotocol/inspector --cli \
  uv run flin-google-search-console-mcp \
  --method tools/call \
  --tool-name get_site_summary \
  --tool-arg site_url=sc-domain:example.com \
  --tool-arg start_date=2026-04-01 \
  --tool-arg end_date=2026-04-20
```

Top queries:

```bash
npx -y @modelcontextprotocol/inspector --cli \
  uv run flin-google-search-console-mcp \
  --method tools/call \
  --tool-name get_top_queries \
  --tool-arg site_url=sc-domain:example.com \
  --tool-arg start_date=2026-04-01 \
  --tool-arg end_date=2026-04-20 \
  --tool-arg row_limit=10
```

Page breakdown:

```bash
npx -y @modelcontextprotocol/inspector --cli \
  uv run flin-google-search-console-mcp \
  --method tools/call \
  --tool-name query_performance \
  --tool-arg site_url=sc-domain:example.com \
  --tool-arg start_date=2026-04-01 \
  --tool-arg end_date=2026-04-20 \
  --tool-arg dimensions='["page"]' \
  --tool-arg row_limit=10
```

URL inspection:

```bash
npx -y @modelcontextprotocol/inspector --cli \
  uv run flin-google-search-console-mcp \
  --method tools/call \
  --tool-name inspect_url \
  --tool-arg site_url=sc-domain:example.com \
  --tool-arg inspection_url=https://example.com/blog/seo-agent
```

## 3) End-to-end test in Claude (uvx)

Use this config:

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

Then ask Claude:

1. `Run health_check`
2. `List my available Search Console sites`
3. `Show me a site summary for the last 28 days`
4. `Show me the top 10 queries`
5. `Inspect https://example.com/some-page`

## 4) Common failures and fixes

`missing_configuration`:

- one or more required env vars are missing
- fix: compare with `.env.example`

`oauth_required`:

- no valid local token exists
- fix: run an auth-required tool and complete browser login

`permission_denied`:

- the OAuth account lacks access to the property
- fix: check Search Console property permissions

`quota_exceeded`:

- the API quota was hit
- fix: retry later or reduce request volume

## Recommended release gate

Before each release:

- `python3 -m pytest`
- `python3 -m compileall src`
- `uv build`
- one live OAuth smoke test
- one Search Analytics smoke test
- one URL Inspection smoke test
