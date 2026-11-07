# flin Google Search Console MCP

## In Claude Desktop starten — Mac mit Apple Silicon (M1 oder neuer)

1. **[Desktop-Paket herunterladen](https://github.com/flin-agency/flin-google-search-console-mcp/releases/latest/download/flin-google-search-console-mcp.mcpb)** und in Claude Desktop unter **Einstellungen → Erweiterungen → Erweiterung installieren** importieren.
2. **Google OAuth Client ID** und **Google OAuth Client Secret** aus dem Passwortmanager bzw. vom zuständigen Administrator eintragen. Optional: die freigegebene Standard-Property. Die Werte gehören zu einem Google-OAuth-Client vom Typ **Desktop-App**; die Search Console API muss aktiviert sein.
3. In Claude: **„Führe connection_status aus.“** Das prüft die lokale Einrichtung, öffnet keinen Browser und ruft Google nicht auf. Bei `incomplete` zuerst die Einstellungen vervollständigen.
4. Danach ausdrücklich: **„Führe list_sites aus und prüfe, ob meine freigegebene Property angezeigt wird.“** Bei Bedarf Google-Anmeldung im Browser abschliessen. Nur ein erfolgreicher Google-Aufruf bestätigt den Zugriff; ein vorhandenes Token genügt dafür nicht.
5. Für den konkreten Datentest: **„Zeige mit get_site_summary die Klicks und Impressionen meiner ausgewählten Property für die letzte abgeschlossene Woche.“** Verwende die Property exakt aus `list_sites`. Ergebnisse können vertrauliche Daten enthalten.

Windows und Intel-Macs bleiben unterstützt; Linux kann den Python-Server direkt
nutzen. Ein automatisierter Paketstart auf Apple Silicon ersetzt keinen echten
Kundenkontotest in der Claude-Oberfläche.

## Updates und Verbindungsstatus

- **Erweiterungsversion**: Version des importierten Starters in Claude.
- **Serverversion**: `connection_status.server_version` bzw. `health_check.server_version`.
- Der aktuelle Starter übernimmt bei Neustart stabile PyPI-Updates innerhalb
  **`>=0.1.8,<0.2`** mit Python 3.12. Vorabversionen und 0.2/1.x sind ausgeschlossen.
  Laufende Sitzungen, OAuth-Einstellungen und gespeicherte Tokens bleiben erhalten.
- Einmaliger Import des aktuellen Pakets ist für ältere Starter nötig, damit die
  Versionsgrenze und das neue Tool-Verzeichnis gelten. Normale kompatible
  Server-Updates brauchen danach keinen Paketimport. Änderungen am Starter,
  an Eingabefeldern oder der Python-Anforderung können einen neuen Import verlangen.
- Start benötigt normalerweise Internet. **Bei Startproblemen:** Verbindung prüfen
  und Claude neu starten; den Cache nicht löschen. Der dokumentierte
  [manuelle Cache-Fallback](docs/desktop-extension.md#startup-fallback) ist nur für
  bereits geladene Pakete verfügbar. Google-Abfragen benötigen weiterhin Internet.

`connection_status` liefert nur `server_version`, `configuration_status`,
`auth_status`, `live_access` und `next_step`. Gespeicherte gültige oder erneuerbare
Tokens ergeben `auth_status=unknown`, solange Google nicht geprüft wurde.
`live_access` bleibt bei diesem rein lokalen Tool immer `not_checked`; `list_sites`
ist ein separater Live-Test und ändert diese lokale Statusaussage nicht.
Das bestehende `health_check` und seine Felder bleiben erhalten.

## Datenumfang und Rechte

Der Server liest Daten; er ändert keine Properties und beantragt keine Indexierung.
Performance-Leserechte genügen für Performance-Abfragen; für den vollständigen
Funktionsumfang einen Full User verwenden. Eine pauschale Owner-Pflicht besteht
nicht. API-Aktivierung und Zugriff auf die konkrete Property sind getrennte
Voraussetzungen. [Google-Rollen](https://support.google.com/webmasters/answer/7687615?hl=en)

Search Analytics liefert Top-Zeilen, **keinen garantierten Voll-Export**. Pro
Anfrage sind maximal 25'000 Zeilen möglich (Standard 1'000); `start_row` ermöglicht
weitere Seiten, hebt Googles interne Grenzen aber nicht auf. Google nennt maximal
50'000 Zeilen pro Tag, Property und Suchtyp. Anonymisierte Suchanfragen fehlen in
Query-Zeilen; Zeilensummen können deshalb von Gesamtsummen abweichen. Fehlende
Zeilen sind kein Nachweis für null Suchanfragen.
[API-Grenzen](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) ·
[Datenauslassungen](https://developers.google.com/search/blog/2022/10/performance-data-deep-dive)

URL Inspection zeigt den Stand im Google-Index, keinen Live-Crawl der Website.
[Google API](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect)

[Datenschutz](PRIVACY.md) · [Sicherheit](SECURITY.md) · [Support](SUPPORT.md)
· [Claude Code Plugin](plugin/README.md) · [Versionierte Downloads](https://github.com/flin-agency/flin-google-search-console-mcp/releases)

## Administrator and developer setup

If your goal is simply "make this work in Claude Desktop", follow these steps in order.

### 1) Make sure the Google account has Search Console access

The Google account you use during login must already have access to at least one Search Console property.

The signed-in account needs access to the selected Search Console property.
Full-user access is sufficient for the full read-only feature set; owner status
is not required. Restricted users can view Performance data and have limited
URL Inspection rights. Google Cloud API enablement does not grant property access.
See [Google's permissions table](https://support.google.com/webmasters/answer/7687615?hl=en).
The OAuth client must be a Desktop app with the Search Console API enabled;
the server requests only `webmasters.readonly`.

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

#### Recommended: desktop extension

Download `flin-google-search-console-mcp-<version>.mcpb` from the
[GitHub releases](https://github.com/flin-agency/flin-google-search-console-mcp/releases)
and open it in a current Claude Desktop version with MCPB UV runtime support.
Alternatively, use **Install Extension** in the desktop extension settings.

Enter the Google OAuth client ID and client secret from step 4 and, optionally,
a default property such as `sc-domain:example.com`. The secret field is marked
sensitive. Continue with the login instructions below. Manual JSON editing is
not required; the Google Cloud setup in steps 1–4 is still required.

The extension runs locally on macOS and Windows. From installer **0.1.8**, it
checks PyPI for the newest stable compatible 0.1-series server release every time the server starts.
Restart Claude Desktop to apply a published server update; no new installer is
needed for ordinary server releases. Running conversations are not hot-updated.
Python 3.12 and server packages are managed by uv. Startup requires internet
access; the installer contains no credentials or saved tokens.

Already installed **0.1.7 or earlier**? Import the current bundle once to apply the compatibility limit
and updated extension metadata. Keep the same OAuth settings; tokens remain outside the extension.
The extension's displayed version describes the launcher. `health_check` returns
`server_version`, the actual running PyPI version.

Changes to Claude's extension settings, permissions, launcher or required Python
version may still require a new bundle. Claude does not auto-update privately
shared manifests from GitHub. A package that drops Python 3.12 support cannot be
used by this launcher; uv selects the latest stable version within `>=0.1.8,<0.2`.

#### Alternative: manual configuration

The existing PyPI installation remains available. Its minimum configuration is:

```json
{
  "mcpServers": {
    "flin-google-search-console-mcp": {
      "command": "uvx",
      "args": ["--refresh-package", "flin-google-search-console-mcp", "--prerelease", "disallow", "flin-google-search-console-mcp>=0.1.8,<0.2"],
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
      "args": ["--refresh-package", "flin-google-search-console-mcp", "--prerelease", "disallow", "flin-google-search-console-mcp>=0.1.8,<0.2"],
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

New token directories are created with private permissions. Existing directories keep
their permissions; on macOS and Linux, they must belong to the current user and
must not be writable by other users. Token files are written with owner-only access.

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
      "args": ["--refresh-package", "flin-google-search-console-mcp", "--prerelease", "disallow", "flin-google-search-console-mcp>=0.1.8,<0.2"],
      "env": {
        "GOOGLE_CLIENT_ID": "your_oauth_client_id",
        "GOOGLE_CLIENT_SECRET": "your_oauth_client_secret",
        "GOOGLE_SEARCH_CONSOLE_TOKEN_PATH": "/absolute/path/to/flin-google-search-console-mcp-token.json"
      }
    }
  }
}
```

### Multiple Google accounts

You can connect multiple Google accounts and choose the account per tool call.

By default, named account tokens are stored next to the default token. To choose a dedicated token directory, set `GOOGLE_SEARCH_CONSOLE_TOKEN_DIR`:

```json
{
  "mcpServers": {
    "flin-google-search-console-mcp": {
      "command": "uvx",
      "args": ["--refresh-package", "flin-google-search-console-mcp", "--prerelease", "disallow", "flin-google-search-console-mcp>=0.1.8,<0.2"],
      "env": {
        "GOOGLE_CLIENT_ID": "your_oauth_client_id",
        "GOOGLE_CLIENT_SECRET": "your_oauth_client_secret",
        "GOOGLE_SEARCH_CONSOLE_TOKEN_DIR": "/absolute/path/to/search-console-tokens"
      }
    }
  }
}
```

Then pass `account` in tool calls:

```json
{
  "tool": "list_sites",
  "args": {
    "account": "work"
  }
}
```

The first call for a new account opens the OAuth browser flow and stores a separate token, for example `work.json`. Account names may contain only letters, numbers, `_`, `-`, and `.`.

An account name must not resolve to the default token file, including case variants
or filesystem aliases. With the default storage layout, `token` is reserved. Omit
`account` to use the default account. Existing named account files remain supported.

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

- `connection_status` (local, no sign-in or Google request)
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
    "account": "work",
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
uv run --env-file .env flin-google-search-console-mcp
```

## Published Package

Run the latest published package directly:

```bash
uvx --refresh-package flin-google-search-console-mcp --prerelease disallow "flin-google-search-console-mcp>=0.1.8,<0.2"
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

## Security

See [the security review](docs/security-review.md) for checks, fixes and remaining
limitations. Tokens must be private files (0600 on macOS/Linux); legacy token
files with broader permissions must be restricted before use. The extension
is unsigned; SHA256SUMS verifies download integrity, not publisher identity.

## More Docs

- [Operational guide](docs/mcp-usage-guide.md)
- [Testing guide](docs/testing.md)
- [Release checklist](docs/release.md)
- [Desktop extension guide](docs/desktop-extension.md)
- [Directory submission preparation](docs/directory-submission.md)
- [Directory reviewer tests](docs/directory-review-tests.md)

## Release on GitHub + PyPI

This repository publishes automatically with GitHub Actions:

- CI: `.github/workflows/ci.yml`
- Release: `.github/workflows/release.yml` triggered by git tags `v*`

CI tests the Python package, desktop bundle and Claude Code plugin on Linux,
macOS and Windows. It also checks the plugin manifest and rejects stale copies
of the runtime in `plugin/`. A release tag builds all formats, publishes the Python package to PyPI,
verifies the launcher against that published version, and creates a GitHub Release with the `.mcpb`, plugin ZIP,
their checksums and Python distributions. Only Python distributions go to PyPI.

A manual workflow run on a branch only validates and builds downloadable
workflow artifacts. Publishing requires a version tag matching the project,
package, plugin and lockfile versions. Publishing a directory listing requires
the separate process described in the [submission guide](docs/directory-submission.md).

PyPI publication runs automatically for each version tag. To retry publishing
an older tag separately, manually run Release on that tag with `publish_pypi` enabled.

### 1) Configure PyPI Trusted Publisher

In PyPI project settings for `flin-google-search-console-mcp`, add a Trusted Publisher with:

- Owner: `flin-agency`
- Repository: `flin-google-search-console-mcp`
- Workflow: `release.yml`
- Environment: `pypi`

### 2) Cut a release

Follow the [release checklist](docs/release.md), commit and push the reviewed
changes, then tag the prepared version:

```bash
git tag v0.1.8
git push origin v0.1.8
```
