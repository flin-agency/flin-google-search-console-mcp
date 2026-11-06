# Claude Desktop Extension

Install the `.mcpb` once in Claude Desktop on macOS or Windows. Starting with
installer **0.1.7**, the bundle is a small stable launcher using MCPB 0.4's UV
runtime. The server comes from PyPI and updates at every server start.

## Installation

1. Enable the Search Console API and create a Google Cloud Desktop OAuth client
   as described in the [README](../README.md).
2. Download the `.mcpb` from the [latest GitHub Release](https://github.com/flin-agency/flin-google-search-console-mcp/releases/latest).
3. In a current Claude Desktop, use **Install Extension** in extension settings.
4. Enter your OAuth client ID and secret, optionally a default property.
5. Ask Claude for `health_check` and `list_sites`, then sign in with Google.

## Automatic server updates

The manifest invokes `uv tool run --from flin-google-search-console-mcp@latest`
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

**Migration from 0.1.6 or earlier:** install 0.1.7 once. Versions through 0.1.5
are frozen; 0.1.6 can keep a stale cached tool environment. Version 0.1.7 explicitly
revalidates it on every start. The old launcher cannot change itself remotely. Keep the same extension name and Google
OAuth settings. Claude may ask you to confirm replacing the extension.

This updates Python server code, not Claude's stored extension manifest. New
settings, permissions, launcher changes or a different Python requirement may
still need a bundle update. uv selects the newest compatible stable release;
a future server requiring Python newer than 3.12 needs a new launcher. The separate
Claude Code plugin remains versioned and locked.

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
