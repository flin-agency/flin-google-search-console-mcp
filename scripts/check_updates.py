"""Prove the installed launcher discovers a newer stable release on its next start.

A private local index serves tiny fixture wheels; no real packages are published,
no Google credentials are read, and the fixture never launches the MCP server.
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "flin-google-search-console-mcp"
MODULE = "flin_google_search_console_mcp"


class QuietHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Fixture updates happen within one second; avoid coarse mtime-based 304s.
        if "If-Modified-Since" in self.headers:
            del self.headers["If-Modified-Since"]
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "public, max-age=86400")
        super().end_headers()

    def log_message(self, *_args):
        pass


def add_release(index: Path, version: str) -> None:
    filename = f"{MODULE}-{version}-py3-none-any.whl"
    metadata = f"{MODULE}-{version}.dist-info"
    with zipfile.ZipFile(index / filename, "w") as archive:
        archive.writestr(f"{metadata}/METADATA", f"Metadata-Version: 2.1\nName: {NAME}\nVersion: {version}\n")
        archive.writestr(f"{metadata}/WHEEL", "Wheel-Version: 1.0\nGenerator: flin-test\nRoot-Is-Purelib: true\nTag: py3-none-any\n")
        archive.writestr(f"{metadata}/RECORD", "")
    links = '\n'.join(f'<a href="{p.name}">{p.name}</a>' for p in sorted(index.glob('*.whl')))
    (index / "index.html").write_text(links, encoding="utf-8")


def main() -> None:
    uv = shutil.which("uv")
    assert uv, "uv is required"
    manifest = json.loads((ROOT / "mcpb/manifest.template.json").read_text())
    with tempfile.TemporaryDirectory(prefix="flin update test ") as temporary:
        root = Path(temporary)
        index = root / "simple" / NAME
        index.mkdir(parents=True)
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(root)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            args = manifest["server"]["mcp_config"]["args"].copy()
            assert args[args.index("--from") + 1] == NAME + ">=0.1.8,<0.2"
            args[args.index("--default-index") + 1] = f"http://127.0.0.1:{server.server_port}/simple"
            args[-1:] = ["-c", (
                "import os; from pathlib import Path; from importlib.metadata import version; "
                "assert os.environ['GOOGLE_CLIENT_ID'] == 'fixture-client'; "
                "assert os.environ['GOOGLE_CLIENT_SECRET'] == 'fixture-secret'; "
                "assert Path(os.environ['GOOGLE_SEARCH_CONSOLE_TOKEN_PATH']).read_text() == 'fixture-token'; "
                f"print(version('{NAME}'))"
            )]
            env = {k: v for k, v in os.environ.items() if not k.startswith(("UV_", "PIP_", "GOOGLE_"))}
            env.update(UV_CACHE_DIR=str(root / "cache"), UV_TOOL_DIR=str(root / "tools"))
            if "UV_PYTHON_INSTALL_DIR" in os.environ:
                env["UV_PYTHON_INSTALL_DIR"] = os.environ["UV_PYTHON_INSTALL_DIR"]
            token = root / "existing-token.json"
            token.write_text("fixture-token")
            token.chmod(0o600)
            before = (token.read_bytes(), token.stat().st_mtime_ns, token.stat().st_mode)
            env.update(GOOGLE_CLIENT_ID="fixture-client", GOOGLE_CLIENT_SECRET="fixture-secret",
                       GOOGLE_SEARCH_CONSOLE_TOKEN_PATH=str(token))
            def launch() -> str:
                return subprocess.check_output([uv, *args], env=env, text=True, timeout=120).strip()
            add_release(index, "0.1.8")
            assert launch() == "0.1.8"
            add_release(index, "0.1.9")
            add_release(index, "0.1.10rc1")
            add_release(index, "0.2.0")
            add_release(index, "1.0.0")
            assert launch() == "0.1.9", "Must bypass the cached version and exclude prereleases"
            assert launch() == "0.1.9", "Repeated launches must keep working without a new installer"
            server.shutdown()
            server.server_close()
            refresh_index = args.index("--refresh-package")
            del args[refresh_index:refresh_index + 2]
            args.insert(2, "--offline")
            assert launch() == "0.1.9", "Explicit offline fallback must use the cached compatible release"
            assert (token.read_bytes(), token.stat().st_mtime_ns, token.stat().st_mode) == before
            print("Same launcher: 0.1.8 -> 0.1.9; prerelease/0.2/1.0 excluded; credentials and token unchanged; offline cache fallback verified.")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    main()
