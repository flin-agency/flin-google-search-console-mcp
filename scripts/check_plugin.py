"""Launch the packaged plugin with dummy configuration and no access to saved tokens."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import zipfile

from mcp import StdioServerParameters

try:
    from .check_mcpb import verify_server
except ImportError:
    from check_mcpb import verify_server


async def check_plugin(bundle: Path) -> None:
    if bundle.is_dir():
        candidates = list(bundle.glob("*.zip"))
        if len(candidates) != 1:
            raise ValueError("The directory must contain exactly one plugin ZIP.")
        bundle = candidates[0]
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("Install uv before running the plugin smoke test.")
    with tempfile.TemporaryDirectory(prefix="flin plugin smoke ") as temporary:
        working = Path(temporary)
        root = working / "plugin"
        with zipfile.ZipFile(bundle) as archive:
            for entry in archive.infolist():
                path = PurePosixPath(entry.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in entry.filename or ":" in entry.filename:
                    raise ValueError("Plugin contains an unsafe archive path.")
            archive.extractall(root)
        manifest = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        config = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["flin-search-console"]
        substitutions = {
            "CLAUDE_PLUGIN_ROOT": str(root),
            "CLAUDE_PLUGIN_DATA": str(working / "plugin-data"),
            "user_config.google_client_id": "smoke-test-client-id",
            "user_config.google_client_secret": "smoke-test-client-secret",
            "user_config.default_site_url": "sc-domain:example.com",
        }

        def substitute(value: str) -> str:
            for name, replacement in substitutions.items():
                value = value.replace("${" + name + "}", replacement)
            if "${" in value:
                raise ValueError("Unresolved plugin variable.")
            return value

        token_dir = working / "test-tokens"
        environment = {key: substitute(value) for key, value in config["env"].items()}
        environment.update({
            "GOOGLE_SEARCH_CONSOLE_TOKEN_PATH": str(token_dir / "token.json"),
            "GOOGLE_SEARCH_CONSOLE_TOKEN_DIR": str(token_dir),
        })
        for key in ("UV_CACHE_DIR", "UV_PYTHON_INSTALL_DIR"):
            if key in os.environ:
                environment[key] = os.environ[key]
        assert config["command"] == "uv"
        await verify_server(StdioServerParameters(
            command=uv, args=[substitute(value) for value in config["args"]], env=environment,
        ))
        assert not token_dir.exists(), "Smoke test must not log in or write OAuth tokens."
        assert not (root / "runtime/.venv").exists(), "Dependencies must stay outside the plugin."
        print(f"Plugin {manifest['version']}: 9 read-only tools, configuration and error responses verified.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    asyncio.run(check_plugin(parser.parse_args().bundle.resolve()))


if __name__ == "__main__":
    main()
