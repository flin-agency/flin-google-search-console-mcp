# Privacy Policy — flin Search Console

Prepared 15 October 2026 for version 0.1.5.

Prepared for publisher review before directory submission. The data-handling
description below reflects the software prepared in this repository.

## Publisher and scope

flin GmbH develops this independent, locally running Google Search Console
integration. This policy covers its Python server, desktop extension and Claude
Code plugin. It does not replace the policies of Google, Anthropic, GitHub or
the package-download services used during installation.

Public product support: https://github.com/flin-agency/flin-google-search-console-mcp/issues

Responsible publisher: flin GmbH, Weinbergstrasse 31, 8006 Zürich, Switzerland.
Privacy and security contact: [flin@flin.agency](mailto:flin@flin.agency).
The published company privacy contact is Nicolas Glauser. Company details are
listed in the [imprint](https://flin.agency/impressum/) and
[company privacy policy](https://flin.agency/privacy-policy/).

## Information used

You supply a Google Desktop OAuth client ID and secret and optionally a default
Search Console property. Google sign-in provides access and refresh tokens. The
server requests only `https://www.googleapis.com/auth/webmasters.readonly`.

When you invoke a tool, it processes the selected account label, property, dates,
dimensions, filters, pagination and, for inspection, the URL you ask to inspect.
Google returns property identifiers, permissions, search queries, page URLs,
performance metrics and indexing information. These may be confidential or contain
personal information depending on your property and queries.

## Data flow and sharing

- The server runs on your computer and sends authentication requests to Google
  Accounts and Google's OAuth token service. A temporary local loopback HTTP
  callback handles browser sign-in.
- It sends Search Console query parameters and authorization tokens to Google's
  APIs over HTTPS. It does not fetch the contents of the inspected website.
- It returns results to the MCP client you use. When that client is Claude,
  results can become part of your conversation and be processed by Anthropic
  according to your plan, settings and Anthropic's terms and privacy policy.
- The server contains no flin.agency telemetry, advertising, analytics or hosted
  data-collection endpoint. It does not send OAuth credentials or Search Console
  results to flin.agency. It does not read chat history or unrelated user files.
- Installation may download Python and packages from distribution services;
  those services receive normal connection information such as your IP address.
  GitHub receives requests when you download releases or use its support service.

## Storage and retention

OAuth token JSON files are stored locally at these default locations:

- macOS: `~/Library/Application Support/flin-google-search-console-mcp/`
- Windows: `%APPDATA%\flin-google-search-console-mcp\`
- Linux: `~/.config/flin-google-search-console-mcp/`

The default account uses `token.json`; named accounts use separate JSON files.
A token file can contain a refresh token, access token, expiry, scope, client ID
and client secret. **These files are not encrypted by this server.** On macOS
and Linux, new directories are private and token files have owner-only permissions.
On Windows, protection depends on the permissions of your user profile; the
server does not configure Windows ACLs. Device backups may also retain copies.

Claude manages the settings you enter. Fields marked sensitive use the client's
secure storage where supported, but Google token JSON files remain separate.
Custom token paths and directories may be configured in manual installations.

The server does not maintain an application database or persist Search Console
result datasets. Tokens remain until you delete them; they may be refreshed
during later requests. Claude conversations, client diagnostic logs and any
exports you create have their own retention settings. The server exposes
sanitized error messages, but client logs should still be treated as private.

## Disconnecting and deletion

Disable the extension or plugin and stop the server. Revoke the application's
access in your Google Account connections settings, then delete the relevant
token files from the storage directory. Remove saved client configuration in
Claude and separately delete conversations or exports if desired.

Uninstalling the extension/plugin alone does not guarantee deletion of the
shared token directory, backups or conversation history. Revocation prevents
future use of the revoked authorization; it does not delete previous results.

## Support requests and changes

Only send the minimum information needed to troubleshoot. Public GitHub issues
are public; never attach tokens, client secrets, private queries or customer data.
We may update this policy when the implementation changes and publish the update
alongside the source and release.

Third-party information: [Google Privacy Policy](https://policies.google.com/privacy),
[Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy),
[Google Account connections](https://myaccount.google.com/connections).
