"""Regressions for modern packaging and Python URL conversion."""

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

from fs._url_tools import url_quote
from fs.opener.errors import EntryPointError
from fs.opener.registry import Registry


def test_external_opener_from_distribution_metadata(tmp_path, monkeypatch):
    plugin = tmp_path / "example_plugin.py"
    plugin.write_text(
        "from fs.opener import Opener\n"
        "from fs.memoryfs import MemoryFS\n"
        "class ExampleOpener(Opener):\n"
        "    protocols = ['example']\n"
        "    def open_fs(self, *args, **kwargs):\n"
        "        return MemoryFS()\n"
        "not_a_class = object()\n"
    )
    dist = tmp_path / "example_plugin-1.0.dist-info"
    dist.mkdir()
    (dist / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: example-plugin\nVersion: 1.0\n"
    )
    (dist / "entry_points.txt").write_text(
        "[fs.opener]\nexample = example_plugin:ExampleOpener\n"
        "invalid = example_plugin:not_a_class\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    try:
        registry = Registry(load_extern=True)
        assert "example" in registry.protocols
        with registry.open_fs("example://") as storage:
            storage.writetext("hello.txt", "안녕하세요")
            assert storage.readtext("hello.txt") == "안녕하세요"
        with pytest.raises(EntryPointError, match="did not return an opener"):
            registry.get_opener("invalid")
        assert "example" not in Registry(load_extern=False).protocols
    finally:
        sys.modules.pop("example_plugin", None)


def test_namespace_extensions_and_no_pkg_resources(tmp_path):
    extension = tmp_path / "fs" / "opener"
    extension.mkdir(parents=True)
    (tmp_path / "fs" / "fs_next_test_extension.py").write_text("VALUE = 42\n")
    (extension / "fs_next_test_extension.py").write_text("VALUE = 43\n")
    script = """
import importlib.abc
import sys
class BlockLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'pkg_resources':
            raise AssertionError('runtime must not import pkg_resources')
sys.meta_path.insert(0, BlockLegacy())
sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[2])
from fs import open_fs
from fs.fs_next_test_extension import VALUE
from fs.opener.fs_next_test_extension import VALUE as OPENER_VALUE
assert (VALUE, OPENER_VALUE) == (42, 43)
with open_fs('mem://') as storage:
    storage.writetext('value.txt', 'ok')
    assert storage.readtext('value.txt') == 'ok'
"""
    subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(tmp_path),
            str(Path(__file__).resolve().parents[1]),
        ],
        check=True,
    )


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/tmp/a b#%.txt", "/tmp/a%20b%23%25.txt"),
        ("//server/share/a b", "//server/share/a%20b"),
        ("/tmp/한글", "/tmp/%ED%95%9C%EA%B8%80"),
    ],
)
def test_absolute_path_url_components(path, expected):
    assert url_quote(path) == expected


def test_windows_path_url_components(monkeypatch):
    monkeypatch.setattr("fs._url_tools._WINDOWS_PLATFORM", True)
    assert url_quote(r"C:\My Documents\a.txt") == "C:/My%20Documents/a.txt"
    assert url_quote(r"\\server\share\a b") == "//server/share/a%20b"
