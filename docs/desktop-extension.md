# Claude Desktop Extension

Install the `.mcpb` once in Claude Desktop on macOS or Windows. Starting with
installer **0.1.8**, the bundle is a small stable launcher using MCPB 0.4's UV
runtime. The server comes from PyPI and updates at every server start.

## Installation

1. Enable the Search Console API and create a Google Cloud Desktop OAuth client
   as described in the [README](../README.md).
2. Download the `.mcpb` from the [latest GitHub Release](https://github.com/flin-agency/flin-google-search-console-mcp/releases/latest).
3. In a current Claude Desktop, use **Install Extension** in extension settings.
4. Enter your OAuth client ID and secret, optionally a default property.
5. Ask Claude for `health_check` and `list_sites`, then sign in with Google.

## Automatic server updates

The manifest invokes `uv tool run --from "flin-google-search-console-mcp>=0.1.8,<0.2"`
with Python 3.12, the HTTPS PyPI index and prereleases disabled. From 0.1.7,
`--refresh-package` also explicitly revalidates the server package index cache. uv checks for a
new release on every start, even when an older tool environment is cached.
Packages are cached to avoid unnecessary downloads. Restart Claude after a new
release to use it. Active sessions keep their current server until restarted;
there is no background replacement during a tool call.

No new `.mcpb` installation is needed for normal server updates. The extension UI
shows the launcher version; `health_check.server_version` shows the running
server version. Google settings and tokens persist in their existing locations.
Startup requires an internet connection; there is no offline fallback guarantee.

**Migration from 0.1.7 or earlier:** import the current bundle once for the
version bound and connection_status metadata. Versions through 0.1.5
are frozen; 0.1.6 can keep a stale cached tool environment. Version 0.1.7 explicitly
revalidates it on every start. The old launcher cannot change itself remotely. Keep the same extension name and Google
OAuth settings. Claude may ask you to confirm replacing the extension.

This updates Python server code, not Claude's stored extension manifest. New
settings, permissions, launcher changes or a different Python requirement may
still need a bundle update. uv selects the newest compatible stable 0.1-series release;
a future server requiring Python newer than 3.12 needs a new launcher. The separate
Claude Code plugin remains versioned and locked.

## Compatibility contract

Automatic updates are bounded to `>=0.1.8,<0.2`, not all future versions. The
0.1 patch series must retain Python 3.12, the imported `server.main` entry point,
stdio MCP operation, existing OAuth setting names, account/token storage layout
and existing tool arguments/results. Additive tools are allowed. Breaking any of
these requires a new series and review of the launcher; a version number alone
cannot prove compatibility. Integration tests exclude prereleases and 0.2/1.0.

## Startup fallback

Keep the normal refresh-at-start behavior. If PyPI is unavailable, check internet
access and restart Claude; do not clear the uv cache or delete Google tokens.
For an administrator's manual MCP entry, use `uv` with these arguments to run
only an already cached compatible release:

```json
["tool", "run", "--offline", "--no-config", "--no-env-file", "--python", "3.12",
 "--default-index", "https://pypi.org/simple", "--prerelease", "disallow",
 "--from", "flin-google-search-console-mcp>=0.1.8,<0.2", "flin-google-search-console-mcp"]
```

Retain the same OAuth environment settings and token location; disable the normal
entry while using the fallback to avoid duplicate tools. Offline mode does not
check for new releases and fails if the cache/Python runtime is missing. Google
queries still require internet. Remove `--offline` and restore the normal entry
when connectivity returns. No automatic fallback or cached-login validation is
claimed. The local fixture test covers a populated cache with its index stopped.

## Security and distribution

The bundle includes only its manifest, a small Python entry point, a launcher
`pyproject.toml`, README, privacy/support documents, license and icon. It contains
no frozen server source, server lockfile, credentials or developer dependencies.
`tools_generated` lets Claude discover the tools from the running server.

Automatic updates trust future releases of the project's PyPI account and their
resolved dependencies. Runtime dependencies are no longer frozen by the desktop
bundle's original lockfile. Each release is tested and audited in CI, published
using GitHub/PyPI Trusted Publishing, and tested again through the real launcher
before the GitHub release is created. The bundle remains unsigned; its checksum
is an integrity check, not a publisher signature.

## Build and test

```bash
uv sync --locked --extra dev
npm ci --ignore-scripts
uv build --out-dir dist/python
uv run --locked python scripts/build_mcpb.py
uv run --locked python scripts/check_mcpb.py dist/mcpb --wheel dist/python
uv run --locked python scripts/check_updates.py
```

Use clean output directories or pass exact artifact paths. The smoke test uses
fake configuration and isolated storage; it never signs into Google. After the
version is published on PyPI, omit `--wheel` to verify the distributed command.

## References

- [Claude private extension updates](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [uv latest-version behavior](https://docs.astral.sh/uv/concepts/tools/#tool-versions)
- [MCPB UV manifest](https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md)
