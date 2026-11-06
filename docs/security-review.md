# Security review — v0.1.5 and v0.1.6

## Update model change in v0.1.6

The desktop bundle now runs the newest compatible stable server from PyPI at
startup. Its original server lockfile is no longer a runtime security boundary.
This intentionally trusts future PyPI releases and the dependencies they resolve.
The separate plugin and source/CI environment retain their lockfile. Prereleases
are excluded, the default index is HTTPS PyPI, and the host's unrelated uv config
and `.env` loading are disabled. A same-launcher test verifies upgrades despite
a cached previous version. A post-publication smoke test verifies the real PyPI
route. No updater changes tokens or replaces code inside a running server.

`health_check.server_version` reports the running version. Existing 0.1.5 bundles
require one upgrade to enable this; extension manifest or Python-runtime changes
may still need installation. See [desktop-extension.md](desktop-extension.md).

## Original v0.1.5 review

Reviewed 6 November 2026. Scope: the Python runtime, OAuth and token storage,
all eight tools, desktop bundle and plugin packaging, dependencies, and GitHub
CI/release workflows. This is a source and automated-test review, not an
independent penetration test or a guarantee against unknown vulnerabilities.

## Findings addressed

- Updated the runtime lockfile after the initial dependency audit reported
  vulnerabilities in 13 packages. The desktop runtime uses Python 3.12 and
  `uv --locked`. Raised the MCP minimum to 1.30.0 while retaining the 1.x limit.
- Token reads now reject symlinks, hard links, nonregular files, unsafe parent
  directories, and files readable/writable by other users on POSIX. Reads are
  bounded to 64 KiB and require a JSON object. Existing tokens with excessive
  permissions fail closed; restrict their permissions to 0600 before reuse.
- Token writes use private temporary files and atomic replacement. Removed a
  redundant path-based chmod after replacement. New storage directories use
  0700; existing shared-writable or foreign-owned directories are rejected.
- OAuth explicitly enables PKCE, listens on 127.0.0.1, uses the OAuth library's
  state validation, and stops waiting after five minutes. Blank OAuth settings
  are rejected. Authorization URLs are not printed into the MCP stream.
- Bundle staging rejects symlinked input ancestors and uses a runtime file
  allowlist. Local configuration, tokens, Git metadata and Node tools are excluded.
- Updated node-forge and forced tmp 0.2.7 in the build tool lockfile.
- GitHub Actions are pinned to commit hashes; job permissions are limited.
  Runtime dependency auditing is required by CI and release builds. PyPI
  publication is opt-in and cannot block the GitHub installer release.

## Verified design boundaries

The only requested Google scope is `webmasters.readonly`. The tools call sites
listing, Search Analytics query and URL Inspection; they expose no Search
Console mutations, shell execution, arbitrary file access or arbitrary URL
fetching. Inspection URLs are passed to Google's API, not fetched by this server.
MCP runs over stdio; only the temporary OAuth callback listens locally.

Error responses use fixed messages and do not echo upstream exceptions,
credentials or token paths. Query/page strings returned by Google are untrusted
data; the MCP client must not treat them as instructions or permissions to use
other tools. The client's access to every account/property authorized by the
selected Google account remains intentional.

## Validation

- 119 passing Python tests on macOS, including filesystem, packaging and error-redaction regressions.
- Actual packed desktop bundle launched on macOS from a path containing spaces:
  MCP initialization, all eight tool schemas/annotations, health check and error
  handling, with fake credentials and isolated storage.
- Plugin source-copy checks, official strict manifest validation and packaged
  plugin smoke test; Python wheel/source-distribution builds.
- `pip-audit 2.10.1` against locked Python 3.12 runtime dependencies: no known
  vulnerabilities after updates. CI repeats this check on each target platform.
- Bandit static scan: four low-severity B105 false positives, reviewed as a fixed
  public Google token endpoint and boolean `has_token_file` values; no embedded
  passwords and no medium/high findings.
- Source and final archives checked for accidental credential inclusion.

## Remaining limitations

- `npm audit` still reports **GHSA-mrhx-c7xc-m3w5** for Zod 3.25.76 and its
  dependent `@anthropic-ai/mcpb` 2.1.2. The official MCPB tool requires Zod 3;
  a forced Zod 4 replacement would change its schema API. This is a build-only
  resource-exhaustion risk when parsing oversized, untrusted manifests. Our
  build validates the small, repository-controlled manifest. Neither Node nor
  Zod is shipped in the desktop bundle. Do not use this build environment to
  validate untrusted third-party manifests. Track the upstream fix:
  https://github.com/advisories/GHSA-mrhx-c7xc-m3w5
- Tokens are local plaintext protected by filesystem permissions, not encrypted
  by this server or stored in macOS Keychain. Same-user malware, administrators
  and backups are outside this protection. Windows uses user-profile ACLs.
- The bundle is unsigned. SHA256SUMS detects corruption; it is not a publisher
  signature. Download from this repository's GitHub Release over HTTPS.
- Python and dependencies are downloaded on first launch. Runtime package
  versions and hashes are locked; Python provisioning and build-backend
  bootstrapping are managed by uv and remain external supply-chain boundaries.
- No live Google sign-in or customer-data request is part of the automated tests.
  A first installation in Claude Desktop and live OAuth/API acceptance test must
  still be performed by the user. macOS process-level smoke tests do not prove
  the Claude Desktop UI or every supported CPU/OS combination.

For confidential reports, contact flin@flin.agency. Do not attach tokens or
customer data to public GitHub issues.
