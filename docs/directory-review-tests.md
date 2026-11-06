# Review tests — flin Search Console

Run against an authorized, non-confidential test property with actual Search Console
data. Record package version, Claude Code version, OS and pass/fail outcomes.
Do not store credentials or returned customer data in this repository.

## Setup

1. Install `uv` and a current Claude Code version with plugin `userConfig` support.
2. From the repository root, run `claude --plugin-dir ./plugin`, or extract the
   plugin ZIP and pass its directory with `--plugin-dir`.
3. Complete the plugin configuration prompts with the dedicated Google Desktop
   OAuth client. Confirm the server in `/mcp`.
4. Use the test property's exact identifier as `PROPERTY`, one of its URLs as
   `URL`, and ISO dates with known data as `START` and `END` below.

## Functional coverage

| Tool | Inputs | Expected result |
| --- | --- | --- |
| `health_check` | no arguments | `oauth_required` before login; no browser or Google request from this check |
| `list_sites` | no arguments | Browser OAuth if needed, then accessible properties; test property included |
| `get_site_summary` | `site_url=PROPERTY`, `start_date=START`, `end_date=END`, `data_state=final` | Clicks, impressions, CTR and position; compare with equivalent GSC filters |
| `query_performance` | same property/dates, `dimensions=[date]`, `row_limit=10` | Up to ten daily rows and metadata |
| `get_top_queries` | same property/dates, `row_limit=10` | Up to ten query rows |
| `get_top_pages` | same property/dates, `row_limit=10` | Up to ten page rows |
| `get_dimension_breakdown` | same property/dates, `dimension=device`, `row_limit=10` | Device breakdown |
| `inspect_url` | `site_url=PROPERTY`, `inspection_url=URL` | Google indexing information; no indexing submission |

Empty results can be valid, but a reviewer account must have enough sample data
to verify the core functionality. Select another valid period if necessary.

## Error and persistence checks

- Invalid date: call `query_performance` with `start_date=invalid-date`. Expect an
  MCP error containing `invalid_arguments`, not a successful result or a raw traceback.
- Default storage collision: `health_check` with `account=token` must give a
  controlled `invalid_configuration` error under the default token layout.
- Sign out/revoke only the dedicated test authorization, then test sign-in again.
  Never revoke an employee's unrelated production access as a test.
- Restart Claude Code and list properties again. The token should be reusable or
  refreshable unless Google revoked or expired the authorization.
- Verify the advertised tool annotations: all eight read-only, non-destructive;
  only `health_check` is closed-world. Google-facing tools are open-world.
- Confirm configuration values and live token contents never appear in tool output.

## Automatic checks

`scripts/check_plugin.py` and `scripts/check_mcpb.py` extract and launch the actual
artifacts with dummy credentials and an isolated token directory. They check MCP
startup, all eight tool declarations, annotations, health configuration and error
responses. They do not sign in, read real tokens or request Search Console data.

Use the private submission channel for reviewer access details. Record a result
such as “summary matched the test property” rather than copying private raw data.
