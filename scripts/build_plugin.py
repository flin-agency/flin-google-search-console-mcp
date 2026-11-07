"""Synchronise the reviewable GitHub plugin folder and build an allowlisted ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

try:
    from .build_mcpb import PACKAGE, ROOT, _copy_file, release_version
except ImportError:
    from build_mcpb import PACKAGE, ROOT, _copy_file, release_version


PLUGIN_FILES = (".claude-plugin/plugin.json", ".mcp.json", "README.md")


def plugin_inputs(root: Path) -> dict[str, Path]:
    inputs = {name: root / "plugin" / name for name in PLUGIN_FILES}
    inputs.update({name: root / name for name in ("PRIVACY.md", "LICENSE", "SUPPORT.md", "SECURITY.md")})
    inputs["icon.svg"] = root / "assets" / "icon.svg"
    for name in ("pyproject.toml", "uv.lock", "README.md"):
        inputs[f"runtime/{name}"] = root / name
    inputs["runtime/server.py"] = root / "mcpb" / "server.py"
    source_dir = root / "src" / PACKAGE
    if source_dir.is_symlink():
        raise ValueError("Plugin runtime directory must not be a symlink.")
    for source in sorted(source_dir.rglob("*")):
        if source.is_symlink():
            raise ValueError("Plugin runtime must not contain symlinks.")
        if source.is_file() and source.suffix == ".py":
            inputs[f"runtime/{source.relative_to(root).as_posix()}"] = source
    for source in inputs.values():
        for path in (source, *source.relative_to(root).parents):
            candidate = path if path.is_absolute() else root / path
            if candidate.is_symlink():
                raise ValueError("Plugin inputs must not contain symlinks.")
        if not source.is_file():
            raise ValueError(f"Missing plugin input: {source.relative_to(root)}")
    return inputs


def validate_plugin_metadata(root: Path, *, tag: str | None = None) -> dict:
    manifest = json.loads((root / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
    if manifest["version"] != release_version(root, tag):
        raise ValueError("Plugin and project versions must match.")
    config = json.loads((root / "plugin/.mcp.json").read_text(encoding="utf-8"))
    server = config["mcpServers"]["flin-search-console"]
    if server["command"] != "uv" or "--locked" not in server["args"]:
        raise ValueError("Plugin must use the locked uv runtime.")
    for key in ("google_client_id", "google_client_secret"):
        field = manifest["userConfig"][key]
        if not field.get("sensitive") or not field.get("required") or "default" in field:
            raise ValueError("OAuth values must be required sensitive fields without defaults.")
    return manifest


def sync_plugin(root: Path) -> None:
    """Update generated files only. Commit these alongside the canonical runtime."""
    validate_plugin_metadata(root)
    for name, source in plugin_inputs(root).items():
        destination = root / "plugin" / name
        if source == destination:
            continue
        for ancestor in (destination, *destination.parents):
            if ancestor == root:
                break
            if ancestor.is_symlink():
                raise ValueError("Refusing to synchronise through a symlink.")
        _copy_file(source, destination)


def check_plugin_sync(root: Path, *, tag: str | None = None) -> dict[str, Path]:
    validate_plugin_metadata(root, tag=tag)
    inputs = plugin_inputs(root)
    for name, source in inputs.items():
        destination = root / "plugin" / name
        if any(path.is_symlink() for path in (destination, *destination.parents)):
            raise ValueError("Plugin folder must not contain symlinks.")
        if not destination.is_file() or destination.read_bytes() != source.read_bytes():
            raise ValueError(f"Plugin copy is stale: {name}. Run scripts/build_plugin.py --sync.")
    actual = set()
    for path in (root / "plugin").rglob("*"):
        if path.is_symlink():
            raise ValueError("Plugin folder must not contain symlinks.")
        relative = path.relative_to(root / "plugin")
        if "__pycache__" in relative.parts:
            continue
        if path.is_file():
            actual.add(relative.as_posix())
    if actual != set(inputs):
        raise ValueError("Unexpected plugin files; only declared source files may be distributed.")
    return inputs


def build_plugin(root: Path, output_dir: Path, *, tag: str | None = None) -> Path:
    inputs = check_plugin_sync(root, tag=tag)
    manifest = validate_plugin_metadata(root, tag=tag)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{manifest['name']}-{manifest['version']}.zip"
    with tempfile.TemporaryDirectory(prefix="flin-plugin-build-") as temporary:
        staging = Path(temporary)
        for name, source in inputs.items():
            _copy_file(source, staging / name)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(inputs):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, (staging / name).read_bytes())
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".zip.sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync", action="store_true", help="Update generated files in plugin/ before building.")
    parser.add_argument("--check", action="store_true", help="Verify the committed plugin copies without building.")
    parser.add_argument("--tag", help="Require the Git tag to match the project and plugin version.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist/plugin")
    args = parser.parse_args()
    if args.sync:
        sync_plugin(ROOT)
    if args.check:
        check_plugin_sync(ROOT, tag=args.tag)
        print("Plugin source copies and versions match.")
    else:
        print(build_plugin(ROOT, args.output_dir, tag=args.tag))


if __name__ == "__main__":
    main()
