# Claude Desktop Extension

The `.mcpb` installs this server locally in Claude Desktop on macOS and Windows.
It uses MCPB 0.4's UV runtime and contains a versioned copy of the server plus
`uv.lock`. It is not a hosted HTTP connector.

For a pre-release installation test, see the German
[Claude review checklist](desktop-review.md).

## Installation

1. Complete the Google Cloud setup in the [README](../README.md): enable the
   Search Console API and create a Desktop app OAuth client.
2. Download the `.mcpb` from the matching
   [GitHub Release](https://github.com/flin-agency/flin-google-search-console-mcp/releases).
3. Open it with a current Claude Desktop version, or use **Install Extension**
   in the desktop extension settings.
4. Fill in the client ID and client secret. The default property is optional.
5. Ask Claude to run `health_check`, then list your Search Console sites.
6. Complete Google sign-in in your browser.

First startup downloads Python if needed and installs locked dependencies.
If Claude rejects the UV server type, update Claude Desktop or use the manual
configuration in the README.

## Updates

Download and install the next version's `.mcpb`. Privately distributed extensions
do not update automatically from GitHub. Team administrators can upload a new
version through their custom-extension management interface, retaining the same
extension name.

This bundle does not run the latest PyPI release automatically. The existing
manual `uvx …@latest` option remains available for that update behaviour.
Saved tokens remain in the existing per-user storage directory outside the
extension. When switching from manual installation, use the same OAuth client
and disable the old entry after verification to avoid duplicate tools.

## Build and verify

Use the Node.js version in `.nvmrc`:

```bash
uv sync --locked --extra dev
npm ci --ignore-scripts
uv run --locked python scripts/build_mcpb.py
uv run --locked python scripts/check_mcpb.py dist/mcpb
```

The output is `dist/mcpb/flin-google-search-console-mcp-<version>.mcpb` alongside
`SHA256SUMS`. The pinned official MCPB CLI validates and packs a temporary staging
directory containing only:

- generated `manifest.json` and the desktop `server.py` entry point
- `pyproject.toml`, `uv.lock` and `README.md`
- privacy policy, support information, MIT license and icon
- Python files in `src/flin_google_search_console_mcp/`

Local `.env` files, tokens, Git metadata, tests, virtual environments and Node
dependencies are excluded. Symlinked runtime files are rejected. OAuth settings
are supplied by Claude at runtime and are never included in the bundle.

The smoke test extracts the archive to a path containing spaces, launches the
manifest command, and checks MCP with dummy credentials and an isolated token
location. It never signs in, contacts Search Console or reads existing tokens.
CI runs it on Linux, macOS and Windows.

## Directory submission

The current directory submission route uses a separate Claude Code plugin in
`plugin/`. New MCPB directory listings are no longer accepted according to the
current submission documentation. The plugin has different platform support;
see [directory-submission.md](directory-submission.md) before choosing it.

## References

- [MCPB manifest and UV runtime](https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md)
- [Claude desktop installation and updates](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [Team extension updates](https://support.claude.com/en/articles/12592343-enabling-and-using-the-desktop-extension-allowlist)
