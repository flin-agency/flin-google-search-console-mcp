# MCP 1.x Compatibility Release Design

## Problem

`flin-google-search-console-mcp` imports `FastMCP` from
`mcp.server.fastmcp`, an API provided by MCP 1.x. The package currently
declares `mcp>=1.6.0`, so a fresh `uvx` installation can resolve MCP 2.0,
where that module no longer exists. The server then reports a misleading
missing-dependency error even though MCP is installed.

## Decision

Constrain the runtime dependency to `mcp>=1.6.0,<2` and release the change as
version 0.1.3. This is the smallest safe correction because the server already
works against MCP 1.x and migrating to MCP 2.0 would require a separate API
migration.

## Verification

Add a package-metadata regression test that requires the MCP upper bound,
regenerate `uv.lock`, run the complete test suite, build the wheel, inspect its
dependency metadata, and launch the wheel through a clean `uvx` resolution.

## Out of Scope

- Migrating the server implementation to MCP 2.0.
- Supporting MCP 1.x and 2.x from one release.
- Publishing or pushing the release without separate confirmation.
