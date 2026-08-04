# MCP 1.x Compatibility Release Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restore clean `uvx` startup by preventing resolution of the incompatible MCP 2.x API.

**Architecture:** Keep the existing FastMCP implementation unchanged and express its supported MCP major version in package metadata. Protect that compatibility contract with a metadata-level regression test and validate the built wheel in a fresh tool environment.

**Tech Stack:** Python 3.10+, Hatchling, uv, pytest, MCP Python SDK 1.x

---

### Task 1: Add the packaging compatibility regression

**Files:**
- Modify: `tests/test_package.py`

**Step 1: Write the failing test**

Import `importlib.metadata` and add a test that reads the installed package's
requirements, locates the MCP requirement, and asserts that it contains `<2`.

**Step 2: Run the focused test to verify it fails**

Run: `uv run pytest tests/test_package.py -q`

Expected: FAIL because the current requirement is `mcp>=1.6.0`.

### Task 2: Constrain MCP and prepare version 0.1.3

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`

**Step 1: Make the minimal metadata change**

Set the project version to `0.1.3` and change the dependency to
`mcp>=1.6.0,<2`.

**Step 2: Regenerate the lockfile**

Run: `uv lock`

Expected: the root package metadata contains the MCP upper bound and MCP 1.x
remains selected.

**Step 3: Run the focused test to verify it passes**

Run: `uv run pytest tests/test_package.py -q`

Expected: PASS.

### Task 3: Verify the release artifact

**Files:**
- Verify: `dist/flin_google_search_console_mcp-0.1.3-py3-none-any.whl`

**Step 1: Run the complete test suite and syntax checks**

Run: `uv run pytest`

Expected: all tests pass.

Run: `uv run python -m compileall -q src`

Expected: exit code 0.

**Step 2: Build the distributions**

Run: `uv build`

Expected: version 0.1.3 wheel and source distribution are created.

**Step 3: Inspect wheel dependency metadata**

Read the wheel's `METADATA` and confirm `Requires-Dist: mcp<2,>=1.6.0`.

**Step 4: Smoke-test a clean uvx resolution**

Run the console script from the local 0.1.3 wheel through `uvx` using a fresh
cache directory.

Expected: MCP 1.x is resolved and the server exits cleanly on closed stdin,
without the missing-dependency traceback.
