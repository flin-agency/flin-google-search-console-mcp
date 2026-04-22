# flin-google-search-console-mcp

Read-only MCP server for Google Search Console, built to work well in Claude Desktop with a browser-based OAuth flow and local token storage.

## Claude Desktop Quickstart

If your goal is simply "make this work in Claude Desktop", follow these steps in order.

### 1) Make sure the Google account has Search Console access

The Google account you use during login must already have access to at least one Search Console property.

Accepted access levels for the API include owner, full, and read access.

### 2) Create or choose a Google Cloud project

In Google Cloud:

1. Create a new project or select an existing one.
2. Enable the **Google Search Console API** for that project.

Official references:

- [Search Console API overview](https://developers.google.com/webmaster-tools/about)
- [Search Console API quickstart](https://developers.google.com/webmaster-tools/v1/quickstart/quickstart-python)

### 3) Configure the OAuth consent screen

In Google Cloud, configure the OAuth consent screen for the same project.

For most personal or team setups:

- choose `External`
- keep the app in `Testing` while you validate the integration
- add your own Google account as a **test user**

Important:

- If the app is `External` and still in `Testing`, users must be listed as test users
- Google documents that test-user authorizations in testing mode can expire after 7 days

This MCP only requests one read-only scope:

- `https://www.googleapis.com/auth/webmasters.readonly`

Official references:

- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [OAuth consent screen configuration](https://support.google.com/cloud/answer/13461325?hl=en)
- [Publishing status and test users](https://support.google.com/cloud/answer/15549945?hl=en)

### 4) Create OAuth credentials of type `Desktop app`

Create an OAuth client in the same Google Cloud project:

1. Go to **Credentials**
2. Click **Create client**
3. Choose **Desktop app**
4. Copy the generated:
   - client ID
   - client secret

You do not need to manually wire redirect URIs into Claude Desktop for this MCP. The desktop OAuth flow uses a local loopback callback handled by the running MCP process.

### 5) Add the MCP to Claude Desktop

The minimum Claude Desktop configuration is:

```json
{
  "mcpServers": {
    "flin-google-search-console-mcp": {
      "command": "uvx",
      "args": ["flin-google-search-console-mcp@latest"],
      "env": {
        "GOOGLE_CLIENT_ID": "your_oauth_client_id",
        "GOOGLE_CLIENT_SECRET": "your_oauth_client_secret"
      }
    }
  }
}
```

If you want a default property so you do not have to pass `site_url` every time:

```json
{
  "mcpServers": {
    "flin-google-search-console-mcp": {
      "command": "uvx",
      "args": ["flin-google-search-console-mcp@latest"],
      "env": {
        "GOOGLE_CLIENT_ID": "your_oauth_client_id",
        "GOOGLE_CLIENT_SECRET": "your_oauth_client_secret",
        "GOOGLE_SEARCH_CONSOLE_SITE_URL": "sc-domain:example.com"
      }
    }
  }
}
```

For local development from a checkout:

```json
{
  "mcpServers": {
    "flin-google-search-console-mcp-local": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/flin-google-search-console-mcp",
        "flin-google-search-console-mcp"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "your_oauth_client_id",
        "GOOGLE_CLIENT_SECRET": "your_oauth_client_secret"
      }
    }
  }
}
```

Replace `/absolute/path/to/flin-google-search-console-mcp` with your local checkout path.

### 6) Restart Claude Desktop

After saving the MCP configuration, fully restart Claude Desktop so it reloads the local server definition.

### 7) Complete the first login inside Claude

Start with these prompts:

```text
Run health_check for the Google Search Console MCP and show the full result.
```

```text
List my Search Console sites.
```

On the first authenticated tool call, the MCP opens a browser window. Sign in with the Google account that has Search Console access and approve the request.

After that:

- the token is stored locally
- future access tokens refresh automatically
- you do not need to paste a refresh token into Claude Desktop config

## What the MCP stores locally

The MCP stores a local token JSON file after the first successful login.

Default locations:

- macOS: `~/Library/Application Support/flin-google-search-console-mcp/token.json`
- Linux: `~/.config/flin-google-search-console-mcp/token.json`
- Windows: `%APPDATA%\flin-google-search-console-mcp\token.json`

If you want to override the location:

```json
{
  "mcpServers": {
    "flin-google-search-console-mcp": {
      "command": "uvx",
      "args": ["flin-google-search-console-mcp@latest"],
      "env": {
        "GOOGLE_CLIENT_ID": "your_oauth_client_id",
        "GOOGLE_CLIENT_SECRET": "your_oauth_client_secret",
        "GOOGLE_SEARCH_CONSOLE_TOKEN_PATH": "/absolute/path/to/flin-google-search-console-mcp-token.json"
      }
    }
  }
}
```

## First Prompts To Verify Everything Works

Use these in Claude Desktop after the server is configured.

### Health check

```text
Run health_check for the Google Search Console MCP and show the full result.
```

### Confirm available properties

```text
List my Search Console sites and tell me whether sc-domain:example.com is available.
```

### Quick summary

```text
Run get_site_summary for site_url sc-domain:example.com from 2026-04-01 to 2026-04-20 and show clicks, impressions, ctr, and position.
```

### Top queries

```text
Run get_top_queries for site_url sc-domain:example.com from 2026-04-01 to 2026-04-20 with row_limit 25 and show the top queries by clicks.
```

### Top pages

```text
Run get_top_pages for site_url sc-domain:example.com from 2026-04-01 to 2026-04-20 with row_limit 25 and show the top pages by clicks.
```

### URL inspection

```text
Run inspect_url for site_url sc-domain:example.com and inspection_url https://example.com/.
```

## Property Format: Domain vs URL-prefix

This is one of the most common setup mistakes.

Examples:

- Domain property: `sc-domain:example.com`
- URL-prefix property: `https://www.example.com/`

Use the exact property string returned by `list_sites`. Do not guess.

## What This MCP Exposes

- `health_check`
- `list_sites`
- `get_site_summary`
- `query_performance`
- `get_top_queries`
- `get_top_pages`
- `get_dimension_breakdown`
- `inspect_url`

## Which Tool To Use

Recommended call order:

1. `health_check`
2. `list_sites`
3. `get_site_summary`
4. `get_top_queries` or `get_top_pages`
5. `query_performance` for custom dimensions and filters
6. `inspect_url` for indexability and canonical checks on a specific URL

## Search Analytics Notes

- `query_performance` uses the Search Analytics API under the hood
- Search Analytics returns top rows, not guaranteed full exports
- The MCP maps Google's positional `keys[]` rows into named `dimensions` objects

Supported knobs include:

- `dimensions`
- `filters`
- `search_type`
- `aggregation_type`
- `data_state`
- `row_limit`
- `start_row`

## Example Tool Calls

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

### Query performance with filters

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

## Source Setup

If you want to run the MCP from source:

```bash
uv sync --extra dev
cp .env.example .env
# Fill .env values
uv run flin-google-search-console-mcp
```

## Published Package

Run the latest published package directly:

```bash
uvx flin-google-search-console-mcp@latest
```

## Troubleshooting

`missing_configuration`

- `GOOGLE_CLIENT_ID` or `GOOGLE_CLIENT_SECRET` is missing from the MCP config

`oauth_required`

- no usable token exists yet
- the first browser-based login has not been completed
- the stored refresh token is no longer usable and the browser flow must run again

`permission_denied`

- the Google account used during login does not have access to the Search Console property

No sites returned

- verify that the Google account really has Search Console access
- confirm you logged into the correct Google account in the browser

Google shows an unverified or testing warning

- this is usually expected while the app is in testing mode
- make sure your Google account is added as a test user on the OAuth consent screen

## More Docs

- [Operational guide](docs/mcp-usage-guide.md)
- [Testing guide](docs/testing.md)
- [Release checklist](docs/release.md)

## Release on GitHub + PyPI

This repository publishes automatically with GitHub Actions:

- CI: `.github/workflows/ci.yml`
- Release: `.github/workflows/release.yml` triggered by git tags `v*`

### 1) Configure PyPI Trusted Publisher

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
