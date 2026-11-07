# Privacy — flin Search Console

Updated 7 November 2026. Publisher: flin GmbH, Weinbergstrasse 31, 8006 Zürich,
Switzerland. Privacy contact: **flin@flin.agency**.

The server runs on your computer. OAuth sign-in and token refresh communicate
with Google; Search Console requests send property names, filters, dates and
inspection URLs to Google's APIs over HTTPS. Results return to Claude or your
chosen MCP client and can become part of its conversations. The server does not
fetch inspected webpages, send data to flin, or collect telemetry.

The installer/update process contacts GitHub, PyPI and Python/package download
services. They receive normal connection metadata such as IP addresses, never
your Google credentials from this server. Stable compatible server updates are
checked at startup; code and resolved dependencies can change without reinstalling.

OAuth client settings come from your administrator/password manager. Claude
handles those settings. Google access/refresh tokens are stored separately as
**unencrypted JSON files**, normally in:

- macOS: `~/Library/Application Support/flin-google-search-console-mcp/`
- Windows: `%APPDATA%\flin-google-search-console-mcp\`
- Linux: `~/.config/flin-google-search-console-mcp/`

The default file is `token.json`; named accounts use their account label. Manual
installations can override these paths. macOS/Linux token files require 0600;
Windows protection depends on profile ACLs. The server does not put tokens in
Keychain. It does not persist Search Console result datasets. Tokens remain until
deleted; backups, client logs and conversations have separate retention.

To disconnect, disable the extension and stop its server, revoke access in
[Google Account connections](https://myaccount.google.com/connections), delete the
relevant token files above, and remove saved OAuth settings in Claude. Delete
client conversations/exports and backups separately if needed. Uninstalling alone
does not revoke Google access or remove the shared token directory.

[Detailed background](https://github.com/flin-agency/flin-google-search-console-mcp/blob/main/docs/privacy-details.md)
· [Security](https://github.com/flin-agency/flin-google-search-console-mcp/blob/main/SECURITY.md)
· [Support](https://github.com/flin-agency/flin-google-search-console-mcp/blob/main/SUPPORT.md)
