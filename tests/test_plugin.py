from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import zipfile

import pytest

from scripts.build_mcpb import PACKAGE, ROOT
from scripts.build_plugin import build_plugin, check_plugin_sync, sync_plugin


@pytest.fixture
def plugin_source(tmp_path: Path) -> Path:
    root = tmp_path / "source"
    root.mkdir()
    for name in ("pyproject.toml", "uv.lock", "README.md", "PRIVACY.md", "LICENSE", "SUPPORT.md"):
        shutil.copyfile(ROOT / name, root / name)
    for directory in ("assets", "mcpb", "src", "plugin"):
        shutil.copytree(ROOT / directory, root / directory, ignore=shutil.ignore_patterns("__pycache__", ".venv"))
    sync_plugin(root)
    return root


def test_plugin_is_self_contained_and_excludes_secrets(plugin_source: Path, tmp_path: Path) -> None:
    for name in (".env", "token.json", f"src/{PACKAGE}/token.json"):
        (plugin_source / name).write_text("private-credential-marker", encoding="utf-8")
    output = build_plugin(plugin_source, tmp_path / "output")
    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
        assert ".claude-plugin/plugin.json" in names
        assert "runtime/server.py" in names
        assert f"runtime/src/{PACKAGE}/server.py" in names
        assert "PRIVACY.md" in names and "LICENSE" in names
        assert not any("private-credential-marker" in archive.read(name).decode() for name in names)
        assert not any(name.endswith((".mcpb", ".pyc")) for name in names)
        config = json.loads(archive.read(".mcp.json"))["mcpServers"]["flin-search-console"]
        assert config["env"]["UV_PROJECT_ENVIRONMENT"].startswith("${CLAUDE_PLUGIN_DATA}")
    assert output.with_suffix(".zip.sha256").is_file()


def test_plugin_build_is_reproducible(plugin_source: Path, tmp_path: Path) -> None:
    first = build_plugin(plugin_source, tmp_path / "one").read_bytes()
    assert build_plugin(plugin_source, tmp_path / "two").read_bytes() == first


def test_plugin_refuses_stale_runtime(plugin_source: Path) -> None:
    server = plugin_source / "src" / PACKAGE / "server.py"
    server.write_text(server.read_text() + "\n# new version\n", encoding="utf-8")
    with pytest.raises(ValueError, match="stale"):
        check_plugin_sync(plugin_source)


def test_plugin_refuses_unexpected_files(plugin_source: Path) -> None:
    (plugin_source / "plugin/.env").write_text("secret-marker", encoding="utf-8")
    with pytest.raises(ValueError, match="Unexpected"):
        check_plugin_sync(plugin_source)


def test_plugin_refuses_version_mismatch(plugin_source: Path) -> None:
    manifest_path = plugin_source / "plugin/.claude-plugin/plugin.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["version"] = "9.9.9"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="versions must match"):
        check_plugin_sync(plugin_source)


@pytest.mark.skipif(os.name == "nt", reason="Symlinks require Windows developer mode")
def test_plugin_refuses_symlinked_runtime(plugin_source: Path, tmp_path: Path) -> None:
    source = plugin_source / "src" / PACKAGE / "leak.py"
    source.symlink_to(tmp_path / "secret")
    with pytest.raises(ValueError, match="symlinks"):
        sync_plugin(plugin_source)


def test_plugin_refuses_secret_defaults(plugin_source: Path) -> None:
    path = plugin_source / "plugin/.claude-plugin/plugin.json"
    manifest = json.loads(path.read_text())
    manifest["userConfig"]["google_client_secret"]["default"] = "private-marker"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="without defaults"):
        check_plugin_sync(plugin_source)
