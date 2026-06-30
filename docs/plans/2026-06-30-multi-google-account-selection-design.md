# Multi Google Account Selection Design

## Goal

Allow each MCP tool call to select which connected Google account to use, so different Search Console properties can be queried from one server instance.

## Chosen Approach

Add an optional `account` argument to every Google Search Console tool. When omitted, the server keeps the current behavior and uses the existing default token file. When provided, the account name resolves to a separate token file under a token directory, so `account="work"` and `account="client-a"` can authorize and refresh independently.

## Token Storage

The existing `GOOGLE_SEARCH_CONSOLE_TOKEN_PATH` continues to define the default account token. A new optional `GOOGLE_SEARCH_CONSOLE_TOKEN_DIR` defines where named account tokens are stored. If not set, named account tokens live in the same directory as the default token.

Named account tokens use safe file names derived from the account id:

- allowed characters: letters, numbers, underscore, hyphen, dot
- disallowed values: empty strings, path separators, `.` and `..`
- token path: `<token_dir>/<account>.json`

This avoids letting a tool argument write outside the configured token directory.

## Data Flow

Tool call arguments flow from `server.py` into `search_console.py`, then into `auth.py`.

1. `server.py` accepts `account` on `health_check`, `list_sites`, analytics tools, and `inspect_url`.
2. `search_console.py` passes `account` into `get_search_console_service`.
3. `auth.py` resolves the token path for either the default account or the named account.
4. OAuth, refresh, and token persistence reuse the existing credential handling.

Responses include `account` only when a named account was explicitly requested. This keeps default responses stable while making selected-account calls auditable.

## Error Handling

Invalid account names raise a configuration-style error before any OAuth or file I/O. Missing or expired named account tokens behave like the default token: non-interactive calls report OAuth required, and interactive calls start the browser-based OAuth flow.

## Testing

Tests should cover:

- resolving default and named token paths
- rejecting unsafe account names
- loading named account credentials from separate token files
- passing `account` through service creation for `list_sites`, analytics, and URL inspection
- preserving existing default-account behavior
- documenting the new tool-call shape in README examples
