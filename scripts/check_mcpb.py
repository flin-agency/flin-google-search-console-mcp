"""Smoke-test the actual bundle with its manifest command and isolated fake credentials."""
from __future__ import annotations

import argparse
import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


EXPECTED_TOOLS = {
    "health_check", "list_sites", "get_site_summary", "query_performance",
    "get_top_queries", "get_top_pages", "get_dimension_breakdown", "inspect_url",
}


async def verify_server(parameters: StdioServerParameters, expected_version: str | None = None) -> None:
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=180)) as client:
            await client.initialize()
            response = await client.list_tools()
            assert {tool.name for tool in response.tools} == EXPECTED_TOOLS
            for tool in response.tools:
                assert tool.annotations and tool.annotations.title
                assert tool.annotations.readOnlyHint is True
                assert tool.annotations.destructiveHint is False
                assert tool.annotations.openWorldHint is (tool.name != "health_check")
            health = await client.call_tool("health_check", {})
            assert not health.isError
            if expected_version:
                assert health.structuredContent["server_version"] == expected_version
            assert health.structuredContent["status"] == "oauth_required"
            assert health.structuredContent["default_site_url"] == "sc-domain:example.com"
            failure = await client.call_tool("query_performance", {
                "start_date": "invalid-date", "end_date": "2026-01-31",
            })
            assert failure.isError
            assert "invalid_arguments" in failure.content[0].text


async def check_bundle(bundle: Path, wheel: Path | None = None) -> None:
    if bundle.is_dir():
        candidates = list(bundle.glob("*.mcpb"))
        if len(candidates) != 1:
            raise ValueError("The bundle directory must contain exactly one .mcpb file.")
        bundle = candidates[0]
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("Install uv before running the bundle smoke test.")
    with tempfile.TemporaryDirectory(prefix="flin mcpb smoke ") as temporary:
        root = Path(temporary)
        with zipfile.ZipFile(bundle) as archive:
            for entry in archive.infolist():
                if not (root / entry.filename).resolve().is_relative_to(root.resolve()):
                    raise ValueError("Bundle contains an unsafe archive path.")
            archive.extractall(root)
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        config = manifest["server"]["mcp_config"]
        substitutions = {
            "__dirname": str(root),
            "user_config.google_client_id": "smoke-test-client-id",
            "user_config.google_client_secret": "smoke-test-client-secret",
            "user_config.default_site_url": "sc-domain:example.com",
        }

        def substitute(value: str) -> str:
            for name, replacement in substitutions.items():
                value = value.replace("${" + name + "}", replacement)
            if "${" in value:
                raise ValueError("Unresolved manifest variable.")
            return value

        environment = {key: substitute(value) for key, value in config["env"].items()}
        environment.update({
            "GOOGLE_SEARCH_CONSOLE_TOKEN_PATH": str(root / "test-tokens" / "token.json"),
            "GOOGLE_SEARCH_CONSOLE_TOKEN_DIR": str(root / "test-tokens"),
        })
        for key in ("UV_CACHE_DIR", "UV_PYTHON_INSTALL_DIR"):
            if key in os.environ:
                environment[key] = os.environ[key]
        arguments = [substitute(value) for value in config["args"]]
        if wheel:
            # Test the candidate before publishing, without modifying the bundle.
            arguments[arguments.index("--from") + 1] = str(wheel.resolve())
        parameters = StdioServerParameters(
            command=uv,
            args=arguments,
            env=environment,
        )
        assert {tool["name"] for tool in manifest["tools"]} == EXPECTED_TOOLS
        await verify_server(parameters, manifest["version"])
        assert not (root / "test-tokens").exists(), "Smoke test must never start OAuth or write tokens."
        print(f"Bundle {manifest['version']}: 8 tools, configuration and error responses verified.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--wheel", type=Path, help="Test an unpublished candidate wheel instead of PyPI.")
    args = parser.parse_args()
    wheel = args.wheel
    if wheel and wheel.is_dir():
        candidates = list(wheel.glob("*.whl"))
        if len(candidates) != 1:
            raise ValueError("The wheel directory must contain exactly one wheel.")
        wheel = candidates[0]
    asyncio.run(check_bundle(args.bundle.resolve(), wheel))


if __name__ == "__main__":
    main()
