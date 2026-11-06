# flin Search Console

![flin Search Console icon](icon.svg)

Read Google Search Console performance and URL indexing information in Claude Code.
Explore clicks, impressions, click-through rate, average position, top queries,
top pages, and device or country breakdowns using eight focused tools. The server
requests only Google's `webmasters.readonly` scope. It cannot change properties,
submit sitemaps, request indexing, or edit your website.

This is an independent integration by flin.agency, not a Google or Anthropic product.

## Compatibility and requirements

Use a current Claude Code version (2.1.281 or later recommended) on a local
computer with a browser and `uv` installed. Python 3.12 and locked dependencies
are downloaded on first start if needed. Internet access is required.

This plugin requires secret configuration prompts (`userConfig`), currently
supported by Claude Code. It does not provide tools in ordinary Claude chat or
Cowork. For Claude Desktop chat, use the separate `.mcpb` download in
[GitHub Releases](https://github.com/flin-agency/flin-google-search-console-mcp/releases).
Installing this plugin does not update or migrate an existing desktop extension.

## Set up

1. Use a Google account with access to a Search Console property.
2. Enable the Google Search Console API in a Google Cloud project and create an
   OAuth client of type **Desktop app**. If the consent screen is in Testing mode,
   add the account as a test user. The
   [project setup guide](https://github.com/flin-agency/flin-google-search-console-mcp#claude-desktop-quickstart)
   explains these Google Cloud steps.
3. Enable the plugin in Claude Code and enter the OAuth client ID and secret in
   the configuration prompts. The default property is optional. Never paste
   credentials into a conversation or repository.
4. Ask for a connection check, then ask to list your Search Console properties.
   Complete Google sign-in in the browser if requested. A local loopback callback
   receives the authorization response; no public MCP endpoint is hosted.
5. Choose an exact property from that list for subsequent requests.

OAuth tokens remain in the existing per-user flin Search Console storage outside
the plugin. Use the same OAuth client to reuse an existing login at the default
location. Custom token-path overrides from another installation are not migrated.

## Try these requests

- “Check the flin Search Console connection, then list my properties.”
- “For [PROPERTY], show clicks, impressions, CTR and average position for the last
  complete calendar month.”
- “For [PROPERTY] and that same period, show the top ten queries and top ten pages.”
- “For [PROPERTY], break down the same period by device.”
- “Inspect the indexing status of [URL] within [PROPERTY].”

Replace the bracketed values with a property and URL you are authorized to query.
Search Console may omit or aggregate some rows; sums of top rows need not match
property totals. Tools may refresh or save the local OAuth token while reading data.

## Troubleshooting

- `missing_configuration`: complete the plugin's Google client settings.
- `oauth_required`: ask to list properties and finish Google sign-in.
- `permission_denied`: check property access and Search Console API enablement.
- `invalid_arguments`: check dates, property identifiers, dimensions and filters.
- Tools missing in chat or Cowork: use Claude Code or the separate desktop bundle.
- `uv` not found: install uv and ensure Claude Code can find it on PATH.

## Privacy Policy

Read the bundled [Privacy Policy](PRIVACY.md) for data flows, token storage,
retention and deletion. Google receives the requested API parameters; tool results
are returned to Claude. The server does not send analytics or Search Console data
to flin.agency. Local OAuth token files are not encrypted by this server.

## Support and updates

Use [GitHub Issues](https://github.com/flin-agency/flin-google-search-console-mcp/issues)
for non-sensitive support. See [SUPPORT.md](SUPPORT.md) for safe diagnostic details.
Do not post tokens, secrets or private customer data in an issue.

This package is prepared for submission and is not yet listed in Anthropic's
directory. Directory updates depend on review and publication settings; a GitHub
Release alone does not update installed `.mcpb` files. Distributed under [MIT](LICENSE).
