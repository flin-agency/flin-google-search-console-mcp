# Security

Report vulnerabilities privately to **flin@flin.agency**. Do not post OAuth
secrets, tokens, customer properties or unredacted logs in public issues.

This local stdio server requests only Google's `webmasters.readonly` scope and
exposes no Search Console write operations. Status checks do not contact Google
or start OAuth. Tokens are plaintext JSON protected by owner-only permissions on
macOS/Linux; Windows relies on user-profile ACLs. They are not stored in Keychain
by this server. Claude's sensitive settings are a separate storage mechanism.

The desktop launcher refreshes stable PyPI releases within `>=0.1.8,<0.2`, using
Python 3.12. This boundary assumes the existing stdio entry point, OAuth settings,
account/token layout and tool contracts remain compatible. Breaking these
contracts requires a new compatibility series and launcher review. Dependencies
are resolved by uv; automatic updates trust future publisher releases.

Bundles are unsigned. Download from this repository and verify SHA256SUMS; a
checksum is not a publisher signature. Known build-only limitations and review
scope are recorded in the [security review](https://github.com/flin-agency/flin-google-search-console-mcp/blob/main/docs/security-review.md).

To disconnect: stop/disable the server, revoke access in
[Google Account connections](https://myaccount.google.com/connections), remove its
local token files, then remove saved settings in Claude. See
[privacy and cleanup](https://github.com/flin-agency/flin-google-search-console-mcp/blob/main/PRIVACY.md).
