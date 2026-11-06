# Release Checklist

The workflow creates a GitHub Release
with the desktop extension, Claude Code plugin ZIP, checksums, wheel and source distribution.
Directory publication is separate; see [directory-submission.md](directory-submission.md).

PyPI publishing is optional and separate: manually dispatch `Release` on the
version tag with `publish_pypi` enabled. Tag pushes publish to GitHub only.

## One-time setup

1. Create PyPI project: `flin-google-search-console-mcp`
2. Configure Trusted Publishing in PyPI:
- GitHub owner: `flin-agency`
- Repository: `flin-google-search-console-mcp`
- Workflow: `release.yml`
- Environment: `pypi`
3. Ensure GitHub Actions is enabled for the repository
4. Permit the release job to create GitHub Releases with its `GITHUB_TOKEN`
   (`contents: write`). No separate GitHub token is needed.
5. Install Node.js from `.nvmrc` for local desktop bundle builds.

## Before each release

1. Update the version in `pyproject.toml` and
   `src/flin_google_search_console_mcp/__init__.py` and
   `plugin/.claude-plugin/plugin.json`, then run `uv lock`.
   The desktop manifest takes its version from the project automatically.
   Keep the manifest's extension name stable across releases.
2. Run local checks, replacing `v0.1.5` with the version being released:

```bash
uv sync --locked --extra dev
npm ci --ignore-scripts
uv run --locked python scripts/build_plugin.py --sync
node node_modules/@anthropic-ai/claude-code/cli-wrapper.cjs plugin validate plugin --strict
uv run --locked python -m pytest
uv run --locked python -m compileall src scripts
uv build --out-dir dist/python
uv run --locked python scripts/build_mcpb.py --tag v0.1.5
uv run --locked python scripts/check_mcpb.py dist/mcpb
uv run --locked python scripts/build_plugin.py --tag v0.1.5
uv run --locked python scripts/check_plugin.py dist/plugin
```

Use a clean output directory when preparing another version. The build rejects
inconsistent project/package/lockfile versions or a mismatching release tag.

3. Inspect the bundle contents and install it in Claude Desktop. Complete a live
   OAuth test, one Search Analytics query and one URL Inspection request.
   Automated tests use fake credentials and never start Google sign-in.
   Use the [German Claude review checklist](desktop-review.md) to record results.
4. Commit and push the reviewed changes, then tag the prepared version:

```bash
git tag v0.1.5
git push origin v0.1.5
```

## Workflow behaviour

- `build` runs tests, creates Python distributions in `dist/python/`, then builds
  and validates the desktop bundle in `dist/mcpb/` alongside `SHA256SUMS`, plus
  the Claude Code plugin in `dist/plugin/` with its `.zip.sha256` file.
- The packaged extension is extracted and launched with its manifest command to
  verify the MCP handshake, tool list, configuration and error responses.
- `publish-pypi` sends only the Python files to PyPI via Trusted Publishing,
  only on an explicitly requested manual tag run.
- `publish-github` runs after the build succeeds on a tag push, independently
  of PyPI, and creates a release with all formats.
- A manual workflow run on a branch builds artifacts without publishing. A run
  on a matching version tag can optionally publish to PyPI.
- If GitHub release creation fails after PyPI publication, rerun only failed jobs;
  do not republish the same immutable PyPI version.

## After release

1. Verify GitHub workflow `Release` succeeded
2. If requested separately, verify the package appears on PyPI
3. Check that the GitHub Release includes the `.mcpb` and matching `SHA256SUMS`.
4. Download and install the published bundle in Claude Desktop.
5. Tell desktop users to install the new `.mcpb`; private bundles do not update
   automatically from GitHub.

The bundle is unsigned unless a separate signing process is introduced. Its
checksum detects download corruption; it is not a publisher signature.
