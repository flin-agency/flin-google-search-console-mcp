# Standardisation review — 0.1.8

7 November 2026. Scope: this Search Console repository only.

## Implemented

- Added connection_status without removing legacy tools/fields. It reports only
  version/setup/auth/live-check status and a concrete next step; no secrets or
  property data. It never calls Google, refreshes a token or opens a browser.
- Bounded startup updates to stable `>=0.1.8,<0.2` releases with Python 3.12.
  The compatibility contract covers server.main, stdio, tool signatures, OAuth
  settings and account/token layout; see desktop-extension.md.
- Preserved refresh-at-start behavior. Documented a manual offline-cache fallback,
  without claiming automatic failover or offline Google access.
- Added an identical stable download alias, preserving the existing extension ID
  and versioned downloads. Both filenames are included in SHA256SUMS.
- Short team-oriented Apple Silicon setup; separate Google Cloud/developer setup;
  concise privacy/security/support files. Documented API limits and role differences.

## Executed locally

Host: macOS arm64 (native Apple Silicon); packaged server interpreter: Python 3.12.

- 127 Python tests passed, including local token immutability and sanitized status.
- Official MCPB validation passed; archive started from a temporary path outside
  the source checkout, with spaces, fake OAuth settings and isolated token storage.
  Nine tools, local status, legacy health and error responses verified.
- The same launcher/cache selected fixture 0.1.8 then 0.1.9. It ignored 0.1.10rc1,
  0.2.0 and 1.0.0; OAuth settings and token bytes/mtime/mode remained unchanged.
  With the test index stopped, explicit offline mode used cached 0.1.9.
- Python wheel/sdist built; plugin strict validation and out-of-source startup passed.

GitHub CI and release workflow repeat tests on their configured platforms, audit
the locked dependency graph and verify the actual stable PyPI version before the
GitHub release. Their results are recorded in Actions, separate from the native
Apple Silicon check above.

## Not performed

No real customer account, live Google sign-in, Search Analytics/Inspection request
or Claude Desktop UI installation was tested. These require the user's account
and explicit interactive acceptance. A local token is not proof of live access.

A one-time current bundle import is required for older launchers to receive the
new version bound and manifest metadata. The server-only addition can reach older
0.1.7 launchers through PyPI; their unbounded configuration does not change itself.

Remaining build-only Zod advisory, unsigned bundles and plaintext local tokens
remain documented in SECURITY.md and security-review.md. No broader security
certification is claimed by these tests.
