# Multi Google Account Selection Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add optional per-tool Google account selection while preserving the existing default-account behavior.

**Architecture:** Named accounts resolve to separate OAuth token files. The MCP layer accepts `account`, the Search Console service builder passes it to auth, and auth resolves the correct token path before loading, refreshing, or creating credentials.

**Tech Stack:** Python, pytest, Google OAuth credentials, Google Search Console API client, MCP FastMCP tools.

---

### Task 1: Token Path Resolution

**Files:**
- Modify: `src/flin_google_search_console_mcp/config.py`
- Test: `tests/test_config.py`

**Step 1: Write failing tests**

Add tests that expect:

- `Settings` includes `token_dir`.
- `load_settings` reads `GOOGLE_SEARCH_CONSOLE_TOKEN_DIR`.
- `resolve_token_path(settings, account=None)` returns `settings.token_path`.
- `resolve_token_path(settings, account="work")` returns `settings.token_dir / "work.json"`.
- unsafe account names such as `"../work"` and `""` are rejected.

**Step 2: Run tests**

Run: `pytest tests/test_config.py -v`

Expected: FAIL because token-dir and account resolution do not exist.

**Step 3: Implement minimal config support**

Add `token_dir` to `Settings`, derive it from env or `token_path.parent`, and add a safe `resolve_token_path` helper.

**Step 4: Run tests**

Run: `pytest tests/test_config.py -v`

Expected: PASS.

### Task 2: Auth Named Accounts

**Files:**
- Modify: `src/flin_google_search_console_mcp/auth.py`
- Test: `tests/test_auth.py`

**Step 1: Write failing tests**

Add tests that call `get_credentials(settings=..., account="work", interactive=False)` and verify credentials are loaded from `token_dir / "work.json"`, not the default token. Add a `describe_auth_state(..., account="work")` test for named account state.

**Step 2: Run tests**

Run: `pytest tests/test_auth.py -v`

Expected: FAIL because auth does not accept or resolve `account`.

**Step 3: Implement auth support**

Accept `account` in `get_credentials` and `describe_auth_state`, resolve the token path once, and reuse existing load, refresh, OAuth, and save functions.

**Step 4: Run tests**

Run: `pytest tests/test_auth.py -v`

Expected: PASS.

### Task 3: Search Console Service Propagation

**Files:**
- Modify: `src/flin_google_search_console_mcp/search_console.py`
- Test: `tests/test_search_console.py`

**Step 1: Write failing tests**

Add tests that verify `get_search_console_service(account="work")` calls `get_credentials(account="work")`, and that `query_performance(..., account="work")` / `inspect_url(..., account="work")` return `account: "work"` in the payload when a named account is used.

**Step 2: Run tests**

Run: `pytest tests/test_search_console.py -v`

Expected: FAIL because service creation and result payloads do not know about `account`.

**Step 3: Implement service propagation**

Thread `account` through `get_search_console_service`, `list_sites`, `query_performance`, `get_site_summary`, and `inspect_url`. Add `account` to returned payloads only when non-empty.

**Step 4: Run tests**

Run: `pytest tests/test_search_console.py -v`

Expected: PASS.

### Task 4: MCP Tool Parameters and Docs

**Files:**
- Modify: `src/flin_google_search_console_mcp/server.py`
- Modify: `tests/test_server_tools.py`
- Modify: `README.md`

**Step 1: Write failing tests**

Add server tests confirming each wrapper passes `account` through to its data function and `health_check(account="work")` uses the selected auth state.

**Step 2: Run tests**

Run: `pytest tests/test_server_tools.py -v`

Expected: FAIL because tool wrappers do not accept `account`.

**Step 3: Implement MCP wrapper support and docs**

Add optional `account` parameters to all tools, pass them through, and document named account usage in README.

**Step 4: Run focused and full verification**

Run:

```bash
pytest tests/test_server_tools.py -v
pytest
```

Expected: PASS.
