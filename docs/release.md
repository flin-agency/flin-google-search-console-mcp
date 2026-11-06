# Release checklist

Version tags publish to **PyPI and GitHub**. From 0.1.7, installed desktop
launchers load the latest compatible stable PyPI server on their next start.
Do not publish a server release until it is ready to reach existing users.

## One-time setup

Configure PyPI Trusted Publishing for project `flin-google-search-console-mcp`,
GitHub owner `flin-agency`, repository `flin-google-search-console-mcp`, workflow
`release.yml`, environment `pypi`. Enable Actions and allow the release job to
create GitHub Releases. No stored PyPI API token is required.

## Prepare a release

1. Update versions in `pyproject.toml`, the package `__init__.py` and
   `plugin/.claude-plugin/plugin.json`; run `uv lock`.
2. Keep the desktop extension name stable. Preserve the launcher's entry point
   and Python 3.12 compatibility for automatic updates of existing installations.
3. Synchronise the plugin and run checks with clean output directories:

```bash
uv sync --locked --extra dev
npm ci --ignore-scripts
uv run --locked python scripts/build_plugin.py --sync
uv run --locked python -m pytest
node node_modules/@anthropic-ai/claude-code/cli-wrapper.cjs plugin validate plugin --strict
uv build --out-dir dist/python
uv run --locked python scripts/build_mcpb.py --tag v0.1.7
uv run --locked python scripts/check_mcpb.py dist/mcpb --wheel dist/python
uv run --locked python scripts/check_updates.py
uv run --locked python scripts/check_plugin.py dist/plugin
```

4. Inspect the artifacts and record any live Claude/OAuth acceptance checks.
   Automated tests use dummy credentials only.
5. Commit, push, then tag the matching version:

```bash
git tag v0.1.7
git push origin v0.1.7
```

## Workflow

- Build tests and audits the locked development/runtime graph, creates Python
  distributions, validates the desktop launcher against the candidate wheel,
  verifies automatic upgrades using a private fixture index, and tests the plugin.
- `publish-pypi` publishes the wheel and source distribution with Trusted Publishing.
- `publish-github` then runs the actual launcher against the published PyPI version
  before creating the GitHub release, installer, plugin ZIP and checksums.
- Manual branch runs build only. Manual tag runs with `publish_pypi=true` publish
  to PyPI without trying to recreate an existing GitHub release.
- If a later job fails after PyPI succeeds, rerun failed jobs only. Never attempt
  to overwrite a published version. Correct faulty releases with a new version.

Verify the PyPI version, GitHub assets and downloaded checksum after publication.
Normal server updates need only a Claude restart. Users on 0.1.6 or earlier need
one initial launcher upgrade; changes to the extension manifest or required
Python version can still require a new installer. Private extension manifests
do not update themselves from GitHub.
