from importlib import metadata

from flin_google_search_console_mcp import __version__


def test_package_exposes_version() -> None:
    assert __version__ == metadata.version("flin-google-search-console-mcp")


def test_package_restricts_mcp_to_supported_major_version() -> None:
    dependencies = metadata.requires("flin-google-search-console-mcp")

    assert dependencies is not None
    mcp_dependency = next(
        dependency for dependency in dependencies if dependency.startswith("mcp")
    )
    assert "<2" in mcp_dependency
