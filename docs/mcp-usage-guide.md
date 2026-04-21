# MCP Usage Guide

Use this guide when operating `flin-google-search-console-mcp` from Claude or MCP Inspector.

## Recommended call order

1. Run `health_check`
2. Run `list_sites`
3. If needed, set or pass the correct `site_url`
4. Run `get_site_summary` for a quick baseline
5. Run `get_top_queries` or `get_top_pages` for common investigations
6. Run `query_performance` for custom dimensions, filters, and pagination
7. Run `inspect_url` for URL-level indexability and canonical details

## Auth behavior

- The first auth-required call can open a browser window
- Tokens are stored locally by the MCP
- Access tokens refresh automatically
- If the stored refresh token fails, the MCP requires interactive OAuth again

## Property rules

- Use the exact property string from `list_sites`
- Domain properties look like `sc-domain:example.com`
- URL-prefix properties look like `https://www.example.com/`
- `inspect_url` requires the inspected URL to belong to the property

## Search Analytics usage guidance

- `get_site_summary` is the fastest answer for overall visibility
- `get_top_queries` is the right starting point for keyword questions
- `get_top_pages` is the right starting point for landing-page questions
- `get_dimension_breakdown` is the quick helper for `country`, `device`, `searchAppearance`, or `date`
- `query_performance` is the full-power tool when you need combinations, filters, or paging

## Useful dimensions

- `query`
- `page`
- `date`
- `device`
- `country`
- `searchAppearance`

## Common error handling

`missing_configuration`:

- `GOOGLE_CLIENT_ID` or `GOOGLE_CLIENT_SECRET` is missing

`oauth_required`:

- no usable token exists yet
- the first interactive login has not been completed
- the stored token is no longer usable and the browser flow must run again

`permission_denied`:

- the Google account used during OAuth does not have access to the property

`invalid_site_url`:

- the property string is missing, malformed, or not accessible

`quota_exceeded`:

- the Search Console API refused the request because a quota limit was hit

## Output quality checklist

- Always state which `site_url` was used
- Do not assume a property type from a free-form domain string
- Treat Search Analytics as ranked result sets, not complete exports
- Use `inspect_url` before making hard claims about indexing for a single page
