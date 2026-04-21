# Google Search Console MCP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a read-only Google Search Console MCP with local OAuth token management, Search Analytics tools, and URL Inspection tools, closely mirroring the ergonomics of the Google Ads MCP.

**Architecture:** Use a `FastMCP` server with separate modules for config, auth, Search Console API access, and MCP tools. Keep OAuth on official Google auth libraries and implement a thin Search Console domain layer that normalizes requests and shapes responses for Claude.

**Tech Stack:** Python 3.10+, `mcp`, `google-api-python-client`, `google-auth`, `google-auth-oauthlib`, `pytest`, `uv`, Hatchling

---

### Task 1: Scaffold the package and metadata

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/flin_google_search_console_mcp/__init__.py`
- Create: `tests/conftest.py`

**Step 1: Write the failing test**

Create a minimal import smoke test that imports `flin_google_search_console_mcp`.

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests -q`
Expected: FAIL because the package files do not exist yet.

**Step 3: Write minimal implementation**

Add package metadata, source layout, and an exported `__version__`.

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests -q`
Expected: PASS for the import smoke test.

**Step 5: Commit**

```bash
git add pyproject.toml README.md src tests
git commit -m "feat: scaffold search console mcp package"
```

### Task 2: Add configuration parsing

**Files:**
- Create: `src/flin_google_search_console_mcp/config.py`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

Add tests for:
- missing required env vars
- custom token path handling
- default token path resolution
- optional default site handling

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_config.py -q`
Expected: FAIL because `config.py` does not exist.

**Step 3: Write minimal implementation**

Implement:
- `ConfigurationError`
- `missing_required_env_vars`
- `Settings` dataclass
- `load_settings`

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_config.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/flin_google_search_console_mcp/config.py tests/test_config.py
git commit -m "feat: add runtime configuration"
```

### Task 3: Add OAuth token management

**Files:**
- Create: `src/flin_google_search_console_mcp/auth.py`
- Create: `tests/test_auth.py`

**Step 1: Write the failing test**

Add tests for:
- credentials loaded from token JSON
- expired credentials with refresh token trigger refresh
- missing token file reports interactive auth required
- corrupted token file raises a clean error

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_auth.py -q`
Expected: FAIL because `auth.py` does not exist.

**Step 3: Write minimal implementation**

Implement:
- OAuth scope constant
- token path helpers
- token read / write helpers
- credential acquisition function that loads, refreshes, or runs installed-app auth
- auth status summary helper for `health_check`

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_auth.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/flin_google_search_console_mcp/auth.py tests/test_auth.py
git commit -m "feat: add oauth token management"
```

### Task 4: Build Search Console request normalization and response mapping

**Files:**
- Create: `src/flin_google_search_console_mcp/search_console.py`
- Create: `tests/test_search_console.py`

**Step 1: Write the failing test**

Add tests for:
- dimension normalization
- filter normalization
- search type validation
- query row mapping from `keys[]` to named dimensions
- aggregate summary mapping
- URL inspection mapping

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_search_console.py -q`
Expected: FAIL because `search_console.py` does not exist.

**Step 3: Write minimal implementation**

Implement:
- constants for supported dimensions and enums
- validation helpers
- service construction
- `list_sites`
- `query_performance`
- wrapper helpers for top queries, top pages, summary, and dimension breakdown
- `inspect_url`
- response shaping helpers

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_search_console.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/flin_google_search_console_mcp/search_console.py tests/test_search_console.py
git commit -m "feat: add search console domain layer"
```

### Task 5: Expose MCP tools

**Files:**
- Create: `src/flin_google_search_console_mcp/server.py`
- Create: `tests/test_server_tools.py`

**Step 1: Write the failing test**

Add tests for:
- `health_check`
- `list_sites`
- `get_site_summary`
- `query_performance`
- `get_top_queries`
- `get_top_pages`
- `get_dimension_breakdown`
- `inspect_url`

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_server_tools.py -q`
Expected: FAIL because `server.py` does not exist.

**Step 3: Write minimal implementation**

Expose the `FastMCP` server and map domain helpers to MCP tool payloads with consistent success and error shapes.

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_server_tools.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/flin_google_search_console_mcp/server.py tests/test_server_tools.py
git commit -m "feat: expose search console mcp tools"
```

### Task 6: Complete docs and examples

**Files:**
- Modify: `README.md`
- Create: `docs/mcp-usage-guide.md`
- Create: `docs/testing.md`
- Create: `docs/release.md`

**Step 1: Write the failing test**

No code test. Instead define required doc assertions:
- README includes Claude Desktop config using only client id and client secret
- README explains local token file behavior
- usage guide includes recommended call ordering

**Step 2: Run verification**

Run: `rg -n "GOOGLE_CLIENT_ID|GOOGLE_CLIENT_SECRET|token" README.md docs`
Expected: required setup guidance appears.

**Step 3: Write minimal implementation**

Document setup, local development, published usage, auth flow, example tool calls, testing, and release flow.

**Step 4: Run verification**

Run: `rg -n "health_check|query_performance|inspect_url" README.md docs`
Expected: core tools are documented.

**Step 5: Commit**

```bash
git add README.md docs
git commit -m "docs: add usage and release guides"
```

### Task 7: Verify build and tests

**Files:**
- Modify only if verification finds issues

**Step 1: Run the full test suite**

Run: `python3 -m pytest -q`
Expected: all tests pass.

**Step 2: Run compile verification**

Run: `python3 -m compileall src`
Expected: no syntax errors.

**Step 3: Build the package**

Run: `python3 -m build`
Expected: source and wheel artifacts are created successfully.

**Step 4: Fix any failures and re-run**

If a command fails, fix the smallest issue and rerun the relevant command before repeating the full verification.

**Step 5: Commit**

```bash
git add -A
git commit -m "chore: finalize google search console mcp"
```
